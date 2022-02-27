from django import template

import shop.models


register = template.Library()

@register.simple_tag
def shop_cart(request):
    return shop.models.Cart.get_session_cart(request)