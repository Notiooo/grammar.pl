from django import template

register = template.Library()


@register.filter(name='next_field')
def next_field(a, field):
    return next(a)[field]