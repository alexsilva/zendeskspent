# coding=utf-8
from django import template
from django.conf import settings
from django.utils import formats


register = template.Library()

__author__ = 'alex'


@register.simple_tag
def get_format(name):
    return formats.get_format(name, lang=settings.LANGUAGE_CODE)