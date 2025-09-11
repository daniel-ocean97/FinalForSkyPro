from datetime import datetime

from django import template

register = template.Library()


@register.filter
def date(value, format_str):
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return value
    if hasattr(value, "strftime"):
        return value.strftime(format_str)
    return value
