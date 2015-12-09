# coding=utf-8
from datetime import date
from calendar import monthrange


def compare_date(a, b, operator):
    if operator(date(a.year, a.month, 1), date(b.year, b.month, 1)):
        return True
    return False


def add_months(date_to_add, months):
    month = date_to_add.month - 1 + months
    year = int(date_to_add.year + month / 12)
    month = month % 12 + 1
    day = min(date_to_add.day, monthrange(year, month)[1])
    return date(year, month, day)
