# coding=utf-8
from django.db import models
from django.utils.lru_cache import lru_cache
import base64
import pickle


class BaseTicket(models.Model):

    @classmethod
    def get_all_field_names(cls, *excluding):
        return [name for name in cls._meta.get_all_field_names() if name not in excluding]

    class Meta(object):
        abstract = True


class Ticket(BaseTicket):
    """ Is a ticket in Zendesk """

    id = models.PositiveIntegerField('ID', primary_key=True)
    url = models.URLField("URL", null=True)

    subject = models.TextField("Assunto")
    status = models.CharField('Estado', max_length=64)

    organization_id = models.PositiveIntegerField(u"Organização (ID)")
    view_id = models.PositiveIntegerField(u"Visualização (ID)")

    _fields = models.TextField("Todos os campos", null=True, default='')

    created_at = models.DateTimeField("Criado em", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True, null=True)

    @property
    def fields(self):
        return pickle.loads(base64.b64decode(self._fields))

    @fields.setter
    def fields(self, value):
        self._fields = base64.b64encode(pickle.dumps(value))

    def get_field_value(self, search_id):
        """ Gets the value of the field by its id
        :raise KeyError
        """
        for items in self.fields:
            if str(items['id']) == str(search_id):
                return items['value']
        raise KeyError('Field id={0!s} not found!'.format(search_id))