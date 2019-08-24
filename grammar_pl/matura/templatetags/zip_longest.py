from django import template
from itertools import zip_longest

register = template.Library()

@register.filter(name='zip_longest')
def zip_list(a, b):
  return zip_longest(a, b)
