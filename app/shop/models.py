from decimal import Decimal

from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Product Model
class Product(models.Model):
    # Detail informations
    name = models.CharField(verbose_name=_("Nom"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    vat = models.PositiveIntegerField(verbose_name=_("TVA (%)"), default=21)
    price = models.DecimalField(verbose_name=_("Prix (HTVA)"), max_digits=15, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")

    def __str__(self):
        return self.name

    def get_description(self):
        if (len(self.description) > 25):
            return "%s..." % self.description[:25]
        return self.description

    def get_incl_tax(self):
        return round(self.price * (1+Decimal(self.vat) / 100), 2)

    def get_picture_url(self):
        return "https://dummyimage.com/450x300/dee2e6/6c757d.jpg"
    
    def get_large_picture_url(self):
        return "https://dummyimage.com/600x700/dee2e6/6c757d.jpg"


# Invoice Models
def generate_invoice_number():
    """
    Generate invoice_number for the Invoice. The number should follow each other.
    """
    code_prefix = timezone.now().strftime("%Y%m")
    last_invoices = Invoice.objects.filter(invoice_number__startswith=code_prefix).values_list('invoice_number', flat=True)
    if len(last_invoices) == 0:
        return "{code_prefix}{code}".format(code_prefix=code_prefix, code=format(1, '04d'))
    else:
        next_code = max(map(int, [i[-4:] for i in last_invoices])) + 1
        return "{code_prefix}{code}".format(code_prefix=code_prefix, code=format(next_code, '04d'))


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('waiting', _("En cours")),
        ('done', _("Payée"))
    )

    # Invoice informations
    invoice_number = models.CharField(verbose_name=_("Numéro"), max_length=255, unique=True, default=generate_invoice_number)
    invoice_date = models.DateField(verbose_name=_("Date de facturation"), default=timezone.now)
    invoice_status = models.CharField(verbose_name=_("Statut"), max_length=25, choices=STATUS_CHOICES, default='waiting')
    
    # Customer informations
    customer = models.ForeignKey('user.User', verbose_name=_("Client"),
        on_delete=models.SET_NULL, blank=True, null=True)
    
    # Contact informations
    contact_first_name = models.CharField(verbose_name=_("Prénom"), max_length=255, blank=True, null=True)
    contact_last_name = models.CharField(verbose_name=_("Nom"), max_length=255, blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_("Adresse e-mail"), blank=True, null=True)
    contact_phone = models.CharField(verbose_name=_("Téléphone"), max_length=255, blank=True, null=True)

    # Address informations
    address = models.CharField(verbose_name=_("Rue / Numéro"), max_length=255, blank=True, null=True)
    address_zipcode = models.CharField(verbose_name=_("Code postal"), max_length=5, blank=True, null=True)
    address_city = models.CharField(verbose_name=_("Ville"), max_length=255, blank=True, null=True)

    # STRIPE Informations
    stripe_payment_intent_id = models.CharField(verbose_name=_('STRIPE PaymentIntent ID'), max_length=30, unique=True, null=True, blank=True)  # Needed when payment via stripe

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")

    def __str__(self):
        return self.invoice_number

    def get_prices(self):
        excl_tax_vat = {}  # calculate excl_tax foreach vat
        for invoiceitem_instance in self.invoiceitem_set.all():
            # Vat
            vat_key = str(invoiceitem_instance.product_vat)
            if vat_key not in excl_tax_vat:
                excl_tax_vat[vat_key] = Decimal('0.00')
            # Price
            excl_tax_vat[vat_key] += invoiceitem_instance.get_total()
        excl_tax = round(sum(excl_tax_vat.values()), 2)

        vat_val = {}
        for vat, val in excl_tax_vat.items():
            vat_val[vat] = round(val * Decimal(vat) / 100, 2)

        return {
            'excl_tax': excl_tax,
            'vat': vat_val,
            'incl_tax': excl_tax + round(sum(vat_val.values()), 2),
        }

    def get_total(self):
        return self.get_prices().get('incl_tax')
    get_total.short_description = _("Montant (TVAC)")


class InvoiceItem(models.Model):
    # Main information
    invoice = models.ForeignKey('Invoice', verbose_name=_("Facture"), on_delete=models.CASCADE)

    # Detail informations
    product = models.ForeignKey('Product', verbose_name=_("Produit"),
        on_delete=models.SET_NULL, blank=True, null=True)
    product_name = models.CharField(verbose_name=_("Nom"), max_length=255)
    product_description = models.TextField(verbose_name=_("Description"))
    product_quantity = models.PositiveIntegerField(verbose_name=_("Quantité"), default=1)
    product_vat = models.PositiveIntegerField(verbose_name=_("TVA (%)"), default=21)
    product_price = models.DecimalField(verbose_name=_("Prix (HTVA)"), max_digits=15, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = _("Facture (Produit)")
        verbose_name_plural = _("Facture (Produits)")

    def __str__(self):
        return "%s - %s" % (self.invoice, self.product_description)

    def get_description(self):
        if (len(self.product_description) > 25):
            return "%s..." % self.product_description[:25]
        return self.product_description

    def get_total(self):
        return round(self.product_quantity * self.product_price, 2)


# Cart Models
class Cart(models.Model):
    class Meta:
        verbose_name = _("Panier")
        verbose_name_plural = _("Paniers")

    # Customer informations
    customer = models.ForeignKey('user.User', verbose_name=_("Client"),
        on_delete=models.SET_NULL, blank=True, null=True)

    # Contact informations
    contact_first_name = models.CharField(verbose_name=_("Prénom"), max_length=255, blank=True, null=True)
    contact_last_name = models.CharField(verbose_name=_("Nom"), max_length=255, blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_("Adresse e-mail"), blank=True, null=True)
    contact_phone = models.CharField(verbose_name=_("Téléphone"), max_length=255, blank=True, null=True)

    # Address informations
    address = models.CharField(verbose_name=_("Rue / Numéro"), max_length=255, blank=True, null=True)
    address_zipcode = models.CharField(verbose_name=_("Code postal"), max_length=5, blank=True, null=True)
    address_city = models.CharField(verbose_name=_("Ville"), max_length=255, blank=True, null=True)

    # Stripe
    stripe_payment_intent_id = models.CharField(verbose_name=_('STRIPE PaymentIntent ID'), max_length=30, unique=True, null=True, blank=True)  # Needed when payment via stripe

    # Active
    is_active = models.BooleanField(verbose_name=_("Est actif?"), default=True)

    class Meta:
        verbose_name = _("Panier")
        verbose_name_plural = _("Paniers")

    @classmethod
    def get_session_cart(cls, request):
        # Accesss current session cart
        session_cart_instance = None
        if 'cart_pk' in request.session and request.session['cart_pk']:
            session_cart_instance = cls.objects.filter(pk=request.session['cart_pk'], is_active=True).first()
        if session_cart_instance is None:
            session_cart_instance = cls.objects.create()

        # If user is connected, check if session cart is user cart.
        cart_instance = session_cart_instance
        if request.user.is_authenticated:
            cart_instance, created = cls.objects.get_or_create(is_active=True, customer=request.user)
            if session_cart_instance.pk != cart_instance.pk:
                # Copy session cart into user cart
                for session_cartitem_instance in session_cart_instance.cartitem_set.all():
                    cartitem_instance = cart_instance.cartitem_set.filter(product=session_cartitem_instance.product).first() if session_cartitem_instance.product else None
                    if cartitem_instance:
                        cartitem_instance.product_quantity = cartitem_instance.product_quantity + session_cartitem_instance.product_quantity
                        cartitem_instance.save()
                    else:
                        cart_instance.cartitem_set.create(
                            product=session_cartitem_instance.product,
                            product_name=session_cartitem_instance.product_name,
                            product_description=session_cartitem_instance.product_description,
                            product_quantity=session_cartitem_instance.product_quantity,
                            product_vat=session_cartitem_instance.product_vat,
                            product_price=session_cartitem_instance.product_price)
                session_cart_instance.is_active = False
                session_cart_instance.save()

        # Save cart intoi session
        request.session['cart_pk'] = cart_instance.pk
        return cart_instance

    def get_items_count(self):
        return sum(self.cartitem_set.values_list('product_quantity', flat=True))

    def is_empty(self):
        return self.get_items_count() == 0

    def get_prices(self):
        excl_tax_vat = {}  # calculate excl_tax foreach vat
        for cartitem_instance in self.cartitem_set.all():
            # Vat
            vat_key = str(cartitem_instance.product_vat)
            if vat_key not in excl_tax_vat:
                excl_tax_vat[vat_key] = Decimal('0.00')
            # Price
            excl_tax_vat[vat_key] += cartitem_instance.get_total()
        excl_tax = round(sum(excl_tax_vat.values()), 2)

        vat_val = {}
        for vat, val in excl_tax_vat.items():
            vat_val[vat] = round(val * Decimal(vat) / 100, 2)

        return {
            'excl_tax': excl_tax,
            'vat': vat_val,
            'incl_tax': excl_tax + round(sum(vat_val.values()), 2),
        }
    
    def get_total(self):
        return self.get_prices().get('incl_tax')
    get_total.short_description = _("Montant (TVAC)")

    def get_billing_informations(self):
        billing_cart = self.get_prices()
        billing_cart['cartitems'] = []
        for cartitem_instance in self.cartitem_set.all():
            billing_cart['cartitems'].append({
                'pk': cartitem_instance.pk,
                'product_quantity': cartitem_instance.product_quantity,
                'product_name': cartitem_instance.product_name,
                'get_description': cartitem_instance.get_description(),
                'get_total': cartitem_instance.get_total(),
            })
        return billing_cart

    def set_product_quantity(self, product_pk, quantity, replace_quantity=True):
        product_instance = Product.objects.get(pk=product_pk)
        cartitem_instance = self.cartitem_set.filter(product=product_instance).first()
        if cartitem_instance:
            cartitem_instance.product_name = product_instance.name
            cartitem_instance.product_description = product_instance.description
            cartitem_instance.product_quantity = quantity if replace_quantity else cartitem_instance.product_quantity + quantity
            cartitem_instance.product_vat = product_instance.vat
            cartitem_instance.product_price = product_instance.price
            cartitem_instance.save()
            if cartitem_instance.product_quantity <= 1:
                cartitem_instance.delete()
        elif quantity >= 1:
            self.cartitem_set.create(
                product=product_instance,
                product_name=product_instance.name,
                product_description=product_instance.description,
                product_quantity=quantity,
                product_vat=product_instance.vat,
                product_price=product_instance.price)
        # billing cart informations
        return self.get_billing_informations()

    def payment_succeeded(self):
        # Create Invoice
        invoice_instance = Invoice.objects.create(
            invoice_status='done',
            customer=self.customer,
            contact_first_name=self.contact_first_name,
            contact_last_name=self.contact_last_name,
            contact_email=self.contact_email,
            contact_phone=self.contact_phone,
            address=self.address,
            address_zipcode=self.address_zipcode,
            address_city=self.address_city,
            stripe_payment_intent_id=self.stripe_payment_intent_id,
        )
        for cartitem_instance in self.cartitem_set.all():
            InvoiceItem.objects.create(
                invoice=invoice_instance,
                product=cartitem_instance.product,
                product_name=cartitem_instance.product_name,
                product_description=cartitem_instance.product_description,
                product_quantity=cartitem_instance.product_quantity,
                product_vat=cartitem_instance.product_vat,
                product_price=cartitem_instance.product_price,
            )
        self.is_active = False
        self.save()

class CartItem(models.Model):
    # Main information
    cart = models.ForeignKey('Cart', verbose_name=_("Panier"), on_delete=models.CASCADE)

    # Detail informations
    product = models.ForeignKey('Product', verbose_name=_("Produit"),
        on_delete=models.SET_NULL, blank=True, null=True)
    product_name = models.CharField(verbose_name=_("Nom"), max_length=255)
    product_description = models.TextField(verbose_name=_("Description"))
    product_quantity = models.PositiveIntegerField(verbose_name=_("Quantité"), default=1)
    product_vat = models.PositiveIntegerField(verbose_name=_("TVA (%)"), default=21)
    product_price = models.DecimalField(verbose_name=_("Prix (HTVA)"), max_digits=15, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = _("Panier (Produit)")
        verbose_name_plural = _("Panier (Produits)")

    def __str__(self):
        return "%s - %s" % (self.cart, self.product_description)

    def get_description(self):
        if (len(self.product_description) > 25):
            return "%s..." % self.product_description[:25]
        return self.product_description

    def get_total(self):
        return round(self.product_quantity * self.product_price, 2)
