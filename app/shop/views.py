import stripe

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, UpdateView

import shop.models
    

# Shop
class ShopView(ListView):
    template_name = "shop/shop.html"
    model = shop.models.Product


class ShopItemView(DetailView):
    template_name = "shop/shop_item.html"
    model = shop.models.Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = shop.models.Product.objects.exclude(pk=self.object.pk)[:4]
        return context

    def post(self, request, *args, **kwargs):
        product = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 1))
        # Find or create cart instance
        cart_instance = shop.models.Cart.get_session_cart(request)
        # Find or create cart item instance
        cart_instance.set_product_quantity(product, quantity)
        # Add message
        messages.add_message(request, messages.INFO, 'Add %s element(s) into your cart.' % quantity)
        return self.get(request, *args, **kwargs)


# Payment
class CartView(DetailView):
    template_name = "shop/cart.html"
    model = shop.models.Cart

    def get_object(self, queryset=None):
        return shop.models.Cart.get_session_cart(self.request)

    def post(self, request, *args, **kwargs):
        product = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 1))
        # Find or create cart instance
        cart_instance = self.get_object()
        # Find or create cart item instance
        cart_instance.set_product_quantity(product, quantity, replace_quantity=True)
        # Add message
        messages.add_message(request, messages.INFO, 'element updated into your cart.')
        return self.get(request, *args, **kwargs)


class CheckoutView(UpdateView):
    template_name = "shop/checkout.html"
    model = shop.models.Cart
    fields = [
        "contact_first_name",
        "contact_last_name",
        "contact_email",
        "contact_phone",
        "address",
        "address_zipcode",
        "address_city",
    ]
    success_url = reverse_lazy('payment')

    def get_object(self, queryset=None):
        return shop.models.Cart.get_session_cart(self.request)


class PaymentView(DetailView):
    template_name = "shop/payment.html"
    model = shop.models.Cart

    def get_object(self, queryset=None):
        return shop.models.Cart.get_session_cart(self.request)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


# Stripe
def stripe_create_payment(request):
    try:
        cart_instance = shop.models.Cart.get_session_cart(request)
        # Create a PaymentIntent with the order amount and currency
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if cart_instance.stripe_payment_intent_id:
            intent = stripe.PaymentIntent.modify(
                cart_instance.stripe_payment_intent_id,
                amount=int(cart_instance.get_total() * 100),
                currency='eur',
            )
        else:
            intent = stripe.PaymentIntent.create(
                amount=int(cart_instance.get_total() * 100),
                currency='eur',
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            # Save PaymentIntent
            cart_instance.stripe_payment_intent_id = intent['id']
            cart_instance.save()
        return JsonResponse({'clientSecret': intent['client_secret']})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_SECRET_WEBHOOK
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'charge.succeeded':
        cart_instance = shop.models.Cart.objects.get(stripe_payment_intent_id=event['data']['object']['payment_intent'])
        cart_instance.payment_succeeded()

    return HttpResponse(status=200)