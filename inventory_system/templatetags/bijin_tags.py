from django import template
import inventory_system.views as views

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''
