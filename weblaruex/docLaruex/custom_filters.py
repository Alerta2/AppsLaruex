from django import template

register = template.Library()

@register.filter
def get_extension(value):
    """
    Devuelve la extensión de un archivo.
    """
    return value.split(".")[-1]
