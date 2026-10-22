import re
from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def texto_plano(valor):
    """Quita el HTML del contenido pero deja un espacio entre párrafos,
    para que los resúmenes no queden pegados ("mundillo.Lo primero...")."""
    texto = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h[1-6]|blockquote)>', ' ', str(valor or ''))
    texto = strip_tags(texto)
    return re.sub(r'\s+', ' ', texto).strip()
