# coding=utf-8
from django.db import models


class CommonBaseModel(models.Model):
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta(object):
        abstract = True


class Company(CommonBaseModel):
    """ Is the enterprise (organization) """
    name = models.CharField("Nome", max_length=256)

    view_external = models.PositiveIntegerField(u"Visualização (ID)")
    estimated_hours_external = models.PositiveIntegerField("Horas estimadas (ID)")
    spent_hours_external = models.PositiveIntegerField("Horas gastas (ID)")

    class Meta(object):
        verbose_name = "Empresa"
        verbose_name_plural = verbose_name + "s"

    def __unicode__(self):
        return self.name


class Contract(CommonBaseModel):
    """ Company contract """
    company = models.ForeignKey(Company, verbose_name=Company._meta.verbose_name)

    name = models.CharField(u"Título", max_length=256)

    archive = models.BooleanField("Arquivar", default=False, help_text=u"Define se o contrato foi cancelado.")

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

    def __unicode__(self):
        print self.dt_start, self.dt_end
        return u"{0.dt_start} até {0.dt_end}".format(self)