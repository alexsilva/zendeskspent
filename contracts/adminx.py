# coding=utf-8
import xadmin
import models

from xadmin.layout import Fieldset, Row
from django.conf import settings


class CompanyAdmin(object):
    list_display = ('name', 'organization_external_list_display')

    form_layout = (
        Fieldset('Dados da empresa',
                 'name',
                 ),
        Fieldset('Referências (Zendesk)',
                 Row('organization_external', 'estimated_hours_external',
                     'spent_hours_external')
                 ),
    )

    def organization_external_list_display(self, obj):
        return '<a href="{0}/organizations/{1.organization_external}" target="_blank"># {1.organization_external}</a>'\
            .format(settings.ZENDESK_BASE_URL, obj)

    organization_external_list_display.short_description = u'Visualizar organização'
    organization_external_list_display.admin_order_field = 'organization_external'
    organization_external_list_display.allow_tags = True


class EmailReportInline(object):
    model = models.EmailContractReport
    extra = 1
    style = 'accordion'

    def __init__(self, request, *args, **kwargs):
        super(EmailReportInline, self).__init__(request, *args, **kwargs)
        if self.queryset().filter(contract=self.org_obj).count() > 0:
            self.extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(EmailReportInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'periods':
            field.queryset = field.queryset.filter(contract=self.org_obj)
        return field


class PeriodInline(object):
    model = models.Period
    extra = 1
    style = 'accordion'

    def __init__(self, request, *args, **kwargs):
        super(PeriodInline, self).__init__(request, *args, **kwargs)
        if self.queryset().filter(contract=self.org_obj).count() > 0:
            self.extra = 0


class ContractAdmin(object):
    list_display = ('name', 'company', 'hours', 'archive_list_display')

    inlines = [EmailReportInline, PeriodInline]
    
    def __init__(self, request, *args, **kwargs):
        super(ContractAdmin, self).__init__(request, *args, **kwargs)
        if hasattr(self, 'org_obj'):
            for i in self.inlines:
                i.org_obj = self.org_obj

    def archive_list_display(self, obj):
        return obj.archive

    archive_list_display.short_description = u"Arquivado"
    archive_list_display.boolean = True
    archive_list_display.admin_order_field = 'archive'


xadmin.site.register(models.Company, CompanyAdmin)
xadmin.site.register(models.Contract, ContractAdmin)
