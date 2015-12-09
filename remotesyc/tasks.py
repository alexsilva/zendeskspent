from __future__ import absolute_import

from celery import shared_task
from django.conf import settings
from django.core import mail
from zdesk import Zendesk
from zdesk.zdesk import ZendeskError

from contracts import utils
from contracts.models import Company, Contract
from contracts import export
from remotesyc.models import Ticket
from remotesyc.utils import compare_date, add_months

from datetime import date
from operator import eq

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


@shared_task(default_retry_delay=10)
def send_email(email):
    email.send()


@shared_task
def report_email():

    date_now = date.today()

    # Percorre cada contrado para enviar o relatorio por contrato
    contracts = Contract.objects.all()
    for contract in contracts:

        # verifica se o contrato esta arquivado ou se possui periodos, senao passa pro proximo
        contract_periods = contract.period_set.all()
        if contract.archive or contract_periods.count() <= 0:
            continue

        # Percorre os emails cadastrados no contrato
        emails = contract.emailcontractreport_set.all()
        last_date = contract_periods.latest('dt_end').dt_end
        for report in emails:

            # Verifica se o dia atual e o mesmo que o especificado para o envio do email
            if report.day_report != date_now.day or report.stop_sending:
                continue

            # informacoes para o email
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [report.email]
            subject = report.title_email
            body = report.text_email
            file_type = report.file_type
            status = report.status
            periods = report.periods.all()
            intervals = {}

            # TODO refatorar para verificar a data corretamente
            # Pega o periodo do mes corrente se nao selecionado e se os periodos nao forem antigos
            if periods.count() <= 0 and not add_months(last_date, 1) <= date_now:
                for i, p in enumerate(contract_periods):
                    _date = add_months(p.dt_end, 1)
                    if compare_date(_date, date_now, eq):
                        periods = [p]
                        break

            # Carrega os tickets da empresa
            tickets = Ticket.objects.filter(organization_id=contract.company.organization_external)

            # Filtra por status
            if not status == Ticket.STATUS.ALL:
                tickets = tickets.filter(status=status)

            # Separa por periodos
            for period in periods:
                t = tickets.filter(updated_at__range=[period.dt_start, period.dt_end])
                if len(t) > 0:
                    intervals[period] = t

            # Verifica se o relatorio vai possui conteudo com os filtros selecionados
            if len(intervals) <= 0:
                break

            # TODO horas imprecisas dependendo dos periodos
            # calculando horas do relatorio
            spent_hours = utils.calc_spent_hours(contract, intervals.values())
            if len(periods) == 1:
                spent_credits = utils.calc_spent_credits(contract, periods[0], status)

                # total de horas validas
                valid_hours = contract.average_hours + spent_credits

                remainder_hours = valid_hours - spent_hours
            else:
                remainder_hours = utils.calc_remainder_hours(contract, spent_hours)

            # Gera o relatorio de acordo com o formato especificado
            attch = getattr(export, 'report_as_'+file_type)(contract, intervals, spent_hours, remainder_hours)

            # Verifica se o email a ser enviado e para o proprio default
            if from_email != to[0]:
                to.append(from_email)

            # Prepara as infos do email
            email = mail.EmailMessage(subject, body, from_email, to)
            email.attach(export.get_filename(contract.company.name, file_type), attch)
            send_email(email)


