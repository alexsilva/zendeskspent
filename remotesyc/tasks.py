from __future__ import absolute_import

from celery import shared_task
from django.conf import settings
from zdesk import Zendesk
from zdesk.zdesk import ZendeskError

from contracts.models import Company
from remotesyc.models import Ticket

__author__ = 'alex'


@shared_task
def sync_remote(*args, **kwargs):
    zendesk = Zendesk(settings.ZENDESK_BASE_URL,
                      settings.ZENDESK_EMAIL, settings.ZENDESK_PASSWORD,
                      api_version=settings.ZENDESK_API_VERSION)

    field_names = Ticket.get_all_field_names('pk', '_fields')
    queryfmt = 'type:ticket organization_id:{0.organization_external}'

    for company in Company.objects.all():
        next_page = True
        page = 1
        registers = []
        while next_page:
            try:
                results = zendesk.search(query=queryfmt.format(company), page=page)
            except ZendeskError as err:
                # view does not exist
                if 'error' in err.msg and err.error_code == 404:
                    break
            if 'results' not in results:
                break
            for ticket in results['results']:
                params = {}
                for name in field_names:
                    params[name] = ticket[name]
                obj = None
                try:
                    obj = Ticket.objects.get(pk=params['id'])
                    for name, value in params.iteritems():  # update
                        setattr(obj, name, value)
                except Ticket.DoesNotExist:
                    obj = Ticket.objects.create(**params)
                finally:
                    obj.fields = ticket['fields']
                    obj.save()
                registers.append(obj.pk)

            next_page = results.get('next_page', False)
            page += 1

        # database clean
        Ticket.objects.filter(organization_id=company.organization_external).exclude(pk__in=registers).delete()

    return Ticket.objects.count()