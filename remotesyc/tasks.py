from __future__ import absolute_import

from celery import shared_task
from django.conf import settings
from zendesk import Zendesk

import contracts.models
import remotesyc.models

__author__ = 'alex'


@shared_task
def sync_remote(*args, **kwargs):
    zendesk = Zendesk(settings.ZENDESK_BASE_URL,
                      settings.ZENDESK_EMAIL, settings.ZENDESK_PASSWORD,
                      api_version=settings.ZENDESK_API_VERSION)

    for company in contracts.models.Company.objects.all():
        next_page = True
        page = 1

        field_names = remotesyc.models.Ticket.get_all_field_names('pk', '_fields', 'view_id')

        registers = []

        while next_page:
            results = zendesk.list_tickets(view_id=company.view_external, page=page)

            for ticket in results['tickets']:
                params = {
                    'view_id': company.view_external
                }
                for name in field_names:
                    params[name] = ticket[name]
                obj = None
                try:
                    obj = remotesyc.models.Ticket.objects.get(pk=params['id'])
                    for name, value in params.iteritems():  # update
                        setattr(obj, name, value)
                except remotesyc.models.Ticket.DoesNotExist:
                    obj = remotesyc.models.Ticket.objects.create(**params)
                finally:
                    obj.fields = ticket['fields']
                    obj.save()
                registers.append(obj.pk)

            next_page = results.get('next_page', False)
            page += 1

        # database clean
        remotesyc.models.Ticket.objects.exclude(pk__in=registers, view_id=company.view_external).delete()

    return remotesyc.models.Ticket.objects.count()