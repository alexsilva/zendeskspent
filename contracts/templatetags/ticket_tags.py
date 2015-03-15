# coding=utf-8
from django import template
from django.conf import settings

from remotesyc.models import Ticket
from contracts import utils

register = template.Library()

__author__ = 'alex'


@register.simple_tag(takes_context=True)
def load_hours(context, ticket, contract):
    return utils.float_number(ticket.get_field_value(contract.company.spent_hours_external))


@register.simple_tag(takes_context=True)
def calc_hours_remainder(context, contract, data):
    """Total de horas restantes para todo o período"""
    spent = calc_hours_spent(context, contract, data)
    if len(data) > 1:
        remainder = contract.hours - spent
    else:
        remainder = contract.average_hours - spent
    return remainder


@register.simple_tag(takes_context=True)
def calc_hours_spent(context, contract, data):
    """Total de horas restantes para todo o período"""
    hours = []
    for key, objects in data.iteritems():
        hours.append(sum([(utils.float_number(ticket.get_field_value(contract.company.spent_hours_external)))
                          for ticket in objects]))
    return sum(hours)


@register.simple_tag(takes_context=True)
def resolve_status(context, ticket):
    return Ticket.STATUS.choices_as_dict()[ticket.status]


@register.filter()
def resolve_id_url(ticket):
    return "{0}/tickets/{1.pk}".format(settings.ZENDESK_BASE_URL, ticket)
