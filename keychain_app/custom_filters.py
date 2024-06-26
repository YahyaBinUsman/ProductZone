from django import template

register = template.Library()

@register.filter
def extract_numeric(value):
    try:
        return int(value.split('_')[-1])
    except (ValueError, IndexError):
        return None
