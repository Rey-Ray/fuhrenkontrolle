from django import template

register = template.Library()

@register.filter(name='is_manager')
def is_manager(obj):
    ans = hasattr(obj, 'manager')
    return ans