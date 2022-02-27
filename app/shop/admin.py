from django.contrib import admin
from django.utils.translation import gettext_lazy as _

import shop.models


@admin.register(shop.models.Product)
class ProductAdmin(admin.ModelAdmin):
    model = shop.models.Product
    list_display = ('name', 'vat', 'price', )
    search_fields = ('name', )
    readonly_fields = ('vat', )

class InvoiceItemInline(admin.TabularInline):
    model = shop.models.InvoiceItem
    verbose_name = _("Produit")
    verbose_name_plural = _("Produits")
    extra = 0
    readonly_fields = ('product_vat', )
    autocomplete_fields = ['product', ]

@admin.register(shop.models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    model = shop.models.Invoice

    list_display = ('invoice_number', 'invoice_date', 'get_total', 'invoice_status', )
    search_fields = ('invoice_number', )
    list_filter = ('customer', 'invoice_status', )
    date_hierarchy = 'invoice_date'

    autocomplete_fields = ['customer', ]
    fieldsets = (
        (_("Client"), {'fields': (
            ('customer', ),
        )}),
        (_("Contact"), {'fields': (
            ('contact_first_name', 'contact_last_name', ),
            'contact_email', 'contact_phone', 
        )}),
        (_("Adresse"), {'fields': (
            'address',
            ('address_zipcode', 'address_city', ),
        )}),
        (_("Facturation"), {'fields': (
            ('invoice_number', 'invoice_status', ),
            'invoice_date', ),
        }),
        (_("Stripe"), {'fields': (
            'stripe_payment_intent_id',
        )}),
    )
    inlines = [InvoiceItemInline, ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CartItemInline(admin.TabularInline):
    model = shop.models.CartItem
    verbose_name = _("Produit")
    verbose_name_plural = _("Produits")
    extra = 0
    readonly_fields = ('product_vat', )
    autocomplete_fields = ['product', ]

@admin.register(shop.models.Cart)
class CartAdmin(admin.ModelAdmin):
    model = shop.models.Cart

    autocomplete_fields = ['customer', ]
    fieldsets = (
        (None, {'fields': ('is_active', )}),
        (_("Client"), {'fields': (
            ('customer', ),
        )}),
        (_("Contact"), {'fields': (
            ('contact_first_name', 'contact_last_name', ),
            'contact_email', 'contact_phone', 
        )}),
        (_("Adresse"), {'fields': (
            'address',
            ('address_zipcode', 'address_city', ),
        )}),
        (_("Stripe"), {'fields': (
            'stripe_payment_intent_id',
        )}),
    )
    inlines = [CartItemInline, ]