from django import template

register = template.Library()

@register.simple_tag
def get_value(data_dict, item_id, date):
    """
    Usage: {% get_value data_dict item.id date %}
    """
    return data_dict.get((item_id, date), "")
