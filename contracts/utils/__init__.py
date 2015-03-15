# coding=utf-8
from contracts import models
import remotesyc.models

__author__ = 'alex'


def float_number(value):
    converted = 0
    if isinstance(value, basestring):
        try:
            converted = float(value.replace(',', '.'))
        except ValueError:
            if value:
                raise
        except TypeError:
            converted = 0
    return converted


def calc_spent_hours(contract, querysets):
    """Total de horas restantes para todo o período"""
    hours = []
    for queryset in querysets:
        hours.append(sum([(float_number(ticket.get_field_value(contract.company.spent_hours_external)))
                          for ticket in queryset]))
    return sum(hours)


def calc_remainder_hours(contract, spent_hours):
    """Total de horas restantes para todo o período"""
    return contract.hours - spent_hours


def calc_spent_credits(contract, period, status=remotesyc.models.Ticket.STATUS.CLOSED):
    """Saldo de horas considerando o consumo dos meses anteriores ao período passado"""
    intervals = models.Period.objects.filter(contract=contract, dt_start__lt=period.dt_start)
    querysets = []
    for interval in intervals:
        querysets.append(remotesyc.models.Ticket.objects.filter(
            organization_id=contract.company.organization_external,
            updated_at__range=[interval.dt_start, interval.dt_end],
            status=status
        ))
    return (contract.average_hours * intervals.count()) - calc_spent_hours(contract, querysets)