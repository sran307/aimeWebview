from django import template
from datetime import datetime
from dateutil.relativedelta import relativedelta
register = template.Library()

@register.simple_tag
def get_value(data_dict, item_id, date, valueType):
    """
    Usage: {% get_value data_dict item.id date %}
    """
    return data_dict.get((item_id, date, valueType), "")

@register.simple_tag
def get_value_2(data_dict, item_id, valueType):
    return data_dict.get((item_id, valueType), "")

@register.filter
def dict_get(d, key):
    if not d:
        return ''
    return d.get(key, 0)

@register.filter
def valuetype_from_desc(desc):
    mapping = {
        'NIC': 'NIC',
        'Prathibha': 'PR',
        'Debt': 'DT',
    }
    return mapping.get(desc, 'OT')

@register.filter
def holdingPeriod(start, end):
    if not start:
        return ""
    if not end:
        end=datetime.today()
    diff = relativedelta(end,start)
    return f"{diff.years} year {diff.months} month {diff.days} days"