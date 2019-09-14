from django import template

register = template.Library()


@register.filter(name='next_field')
def next_field(a, field):
    try:
        return next(a)[field]
    except StopIteration:
        return None