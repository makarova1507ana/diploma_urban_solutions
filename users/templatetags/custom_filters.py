from django import template
from django import template

register = template.Library()

@register.filter
def split_first(value, max_length=10):
    """Возвращает первое слово до пробела и обрезает его, если оно слишком длинное"""
    first_name = value.split(' ')[0]  # Берем первое слово (до пробела)
    if len(first_name) > max_length:
        return first_name[:max_length]  # Обрезаем до max_length
    return first_name
