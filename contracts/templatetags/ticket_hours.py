from django import template

register = template.Library()
__author__ = 'alex'


@register.simple_tag(takes_context=True)
def load_hours(context, ticket, contract):
    return ticket.get_field_value(contract.company.spent_hours_external) or 0.0