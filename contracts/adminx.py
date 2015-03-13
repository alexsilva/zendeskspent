# coding=utf-8
import xadmin
from xadmin.layout import Fieldset, Row
from django.conf import settings

import models


class CompanyAdmin(object):
    list_display = ('name', 'organization_external_list_display')

    form_layout = (
        Fieldset('Dados da empresa',
                 'name',
        ),
        Fieldset('Referências (Zendesk)',
                 Row('organization_external', 'estimated_hours_external',
                     'spent_hours_external')
        )
    )

    def organization_external_list_display(self, obj):
        return '<a href="{0}/organizations/{1.organization_external}" target="_blank"># {1.organization_external}</a>'.format(
            settings.ZENDESK_BASE_URL, obj)

    organization_external_list_display.short_description = u'Visualizar organização'
    organization_external_list_display.admin_order_field = 'organization_external'
    organization_external_list_display.allow_tags = True


class PeriodInline(object):
    model = models.Period
    extra = 2
    style = 'accordion'


class ContractAdmin(object):
    list_display = ('name', 'company', 'hours', 'archive_list_display')

    inlines = [PeriodInline]

    def archive_list_display(self, obj):
        return obj.archive

    archive_list_display.short_description = u"Arquivado"
    archive_list_display.boolean = True
    archive_list_display.admin_order_field = 'archive'


xadmin.site.register(models.Company, CompanyAdmin)
xadmin.site.register(models.Contract, ContractAdmin)
