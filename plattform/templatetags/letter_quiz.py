from django import template

register=template.Library()

@register.filter(name='custom')
def custom(value):
    return chr(64 + value)

