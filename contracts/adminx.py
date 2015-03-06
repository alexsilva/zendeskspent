# coding=utf-8
import xadmin
from xadmin.layout import Fieldset, Row
from django.conf import settings

import models


class CompanyAdmin(object):
    list_display = ('name', 'view_external_list_display')

    form_layout = (
        Fieldset('Dados da empresa',
                 'name',
        ),
        Fieldset('Referências (Zendesk)',
                 Row('view_external', 'estimated_hours_external',
                     'spent_hours_external')
        )
    )

    def view_external_list_display(self, obj):
        return '<a href="{0}/rules/{1.view_external}"># {1.view_external}</a>'.format(settings.ZENDESK_BASE_URL, obj)

    view_external_list_display.short_description = u'Seguir visualização'
    view_external_list_display.admin_order_field = 'view_external'
    view_external_list_display.allow_tags = True


class PeriodInline(object):
    model = models.Period
    extra = 2
    style = 'accordion'


class ContractAdmin(object):
    list_display = ('name', 'company', 'archive_list_display')

    inlines = [PeriodInline]

    def archive_list_display(self, obj):
        return obj.archive

    archive_list_display.short_description = u"Arquivado"
    archive_list_display.boolean = True
    archive_list_display.admin_order_field = 'archive'


xadmin.site.register(models.Company, CompanyAdmin)
xadmin.site.register(models.Contract, ContractAdmin)
