from django.urls import path, include

import shop.views

urlpatterns = [
    # Shop
    path('', shop.views.ShopView.as_view(), name="shop"),
    path('item/<int:pk>/', shop.views.ShopItemView.as_view(), name="shop_item"),

    # Payment
    path('cart/', shop.views.CartView.as_view(), name="cart"),
    path('checkout/', shop.views.CheckoutView.as_view(), name="checkout"),
    path('payment/', shop.views.PaymentView.as_view(), name="payment"),

    # Stripe
    path('stripe-create-payment-intent', shop.views.stripe_create_payment, name="stripe_create_payment"),
    path('stripe-webhook/', shop.views.stripe_webhook, name="stripe_webhook"),
]
