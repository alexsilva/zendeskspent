# coding=utf-8
from django import template

register = template.Library()
__author__ = 'alex'


@register.simple_tag(takes_context=True)
def load_hours(context, ticket, contract):
    return ticket.get_field_value(contract.company.spent_hours_external) or 0.0



@register.simple_tag(takes_context=True)
def calc_hours_remainder(context, contract, data):
    """Total de horas restantes para todo o período"""
    total_hours = contract.hours
    hours = []
    for key, objects in data.iteritems():
        hours.append(sum([(float(ticket.get_field_value(contract.company.spent_hours_external) or 0.0))
                          for ticket in objects]))
    return total_hours - sum(hours)