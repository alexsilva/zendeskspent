# coding=utf-8
from django.conf import settings
from django.db import models
from django.utils import dateformat
from django.utils import formats
from remotesyc.models import BaseTicket


class CommonBaseModel(models.Model):
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta(object):
        abstract = True


class Company(CommonBaseModel):
    """ Is the enterprise (organization) """
    name = models.CharField("Nome", max_length=256)

    organization_external = models.PositiveIntegerField(u"Organização (ID)")
    estimated_hours_external = models.PositiveIntegerField("Horas estimadas (ID)",
                                                           default=settings.COMPANY_ESTIMATED_HOURS_ID)
    spent_hours_external = models.PositiveIntegerField("Horas gastas (ID)",
                                                       default=settings.COMPANY_SPENT_HOURS_ID)

    class Meta(object):
        verbose_name = "Empresa"
        verbose_name_plural = verbose_name + "s"

    def __unicode__(self):
        return self.name


class Contract(CommonBaseModel):
    """ Company contract """
    company = models.ForeignKey(Company, verbose_name=Company._meta.verbose_name)

    name = models.CharField(u"Título", max_length=256)

    hours = models.PositiveIntegerField("Total de horas", help_text="Total de horas contratadas.")

    archive = models.BooleanField("Arquivar", default=False, help_text=u"Define se o contrato foi cancelado.")

    @property
    def average_hours(self):
        try:
            average = self.hours / self.period_set.count()
        except ZeroDivisionError:
            average = 0.0
        return average

    class Meta(object):
        verbose_name = "Contrato"
        verbose_name_plural = verbose_name + "s"

    def __unicode__(self):
        return self.name


class Period(CommonBaseModel):
    """ Contract expiration dates """
    dt_start = models.DateField(u'Início')
    dt_end = models.DateField(u'Término')

    contract = models.ForeignKey(Contract)

    class Meta(object):
        verbose_name = "Data"
        verbose_name_plural = verbose_name + "s"
        ordering = ('dt_start',)

    def __unicode__(self):
        date_format = formats.get_format("DATE_FORMAT", lang=settings.LANGUAGE_CODE)
        return u"{0:s} até {1:s}".format(dateformat.format(self.dt_start, date_format),
                                         dateformat.format(self.dt_end, date_format))


class EmailContractReport(models.Model):

    PDF = 'pdf'
    CSV = 'csv'
    FILE_TYPE_CHOICES = ((PDF, 'PDF'), (CSV, 'CSV'))

    email = models.EmailField(u'E-mail')
    title_email = models.CharField(u'Título do e-mail', default=u'Relatório mensal de horas - Fábrica Digital',
                                   max_length=255)
    text_email = models.TextField(u'Mensagem', default=u'Relatório mensal de horas em anexo Fábrica Digital',
                                  max_length=300)
    day_report = models.PositiveIntegerField(u"Dia do relatório", help_text=u"Dia de envio do relatório em cada mês.",
                                             default=1)
    file_type = models.CharField(u'Formato do relatório', choices=FILE_TYPE_CHOICES,
                                 default=PDF, max_length=10)
    status = models.CharField(u'Status', help_text=u'Filtrar por status do ticket.', choices=BaseTicket.STATUS.CHOICES,
                              default=BaseTicket.STATUS.ALL, max_length=120)
    periods = models.ManyToManyField(Period, verbose_name=u'Períodos', help_text=u'Filtrar por períodos dos tickets.',
                                     blank=True, null=True)
    stop_sending = models.BooleanField(u'Para o envio de relatórios para esse e-mail', default=False)

    contract = models.ForeignKey(Contract)

    class Meta(object):
        verbose_name = 'E-mail'
        verbose_name_plural = u"E-mails dos relatórios"

    def __unicode__(self):
        return self.email


class EmailReportLog(models.Model):
    from_email = models.EmailField(u'De', null=False, blank=False)
    to = models.EmailField(u'Para', null=False, blank=False)
    subject = models.CharField(u'Título', max_length=150,  null=False, blank=False)
    body = models.TextField(u'Mensagem', max_length=255, null=False, blank=False)
    status = models.CharField(u'Status', max_length=20, null=False, blank=False)
    periods = models.ManyToManyField(Period, verbose_name=u'Períodos', null=False, blank=False)
    sent_at = models.DateTimeField(u'Enviado em', auto_now_add=True, null=False, blank=False)

    class Meta(object):
        verbose_name = u'Log de e-mail de relatório'
        verbose_name_plural = u'Logs de e-mails de relatórios'

    def __unicode__(self):
        return self.to
