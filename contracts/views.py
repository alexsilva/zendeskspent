# coding=utf-8
import datetime
import copy
import csv
import StringIO

from django.utils import formats, dateformat

from django.conf import settings
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


styleSheet = getSampleStyleSheet()

import forms
import models
import remotesyc.models
import utils


def datetime_format(value):
    fmt = formats.get_format("DATETIME_FORMAT", lang=settings.LANGUAGE_CODE)
    return dateformat.format(value, fmt)


class ContractView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "contracts/contracts.html", {
            'form': forms.CompanyForm(),
            'form_step': 1
        })

    @staticmethod
    def post_changed(request):
        _post = copy.deepcopy(request.POST)
        if 'status' not in _post:  # Force default
            _post['status'] = remotesyc.models.Ticket.STATUS.CLOSED
        return _post

    @staticmethod
    def get_filename(context, fmt):
        dtstr = datetime.date.today().strftime('%d-%m-%Y')
        return "{0[contract].company}_{1!s}.{2!s}".format(context, dtstr, fmt)

    @staticmethod
    def make_rows(context):
        headers = [
            'subject',
            lambda c, o: datetime_format(o.created_at),
            lambda c, o: datetime_format(o.updated_at),
            utils.load_spent_hours,
            utils.load_estimated_hours
        ]
        rows = []
        for queryset in context['intervals'].values():
            for obj in queryset:
                row = []
                for header in headers:
                    if callable(header):
                        row.append(header(context['contract'], obj))
                    else:
                        row.append(getattr(obj, header))
                rows.append(row)
        return rows

    @classmethod
    def export_as_pdf(cls, request, context):
        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{0!s}"'.format(cls.get_filename(context, 'pdf'))

        # Create the PDF object, using the response object as its "file."
        doc = SimpleDocTemplate(response, pagesize=landscape(A4), title='Relatório de horas')

        rows = [settings.EXPORT_CSV_COLUMNS]
        rows.extend(cls.make_rows(context))

        store = [Paragraph('<para align=center spaceb=3>RELATÓRIO DE HORAS</para>', styleSheet["h3"]),
                 Spacer(1, 0.5 * inch)]

        table = Table(rows)
        table.setStyle(
            TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.gray),
                ('GRID', (0, 0), (-1, 0), 0.25, colors.blue),
                ('ALIGN', (1, 0), (-1, len(rows) - 1), 'CENTER')
            ]))

        store.append(table)
        store.append(Spacer(1, 0.5 * inch))

        resume = Table([
            ['Total de horas', 'Horas gastas', 'Horas restantes'],
            [context['contract'].hours, context['spent_hours'], context['remainder_hours']]
        ])
        resume.setStyle(
            TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.gray),
                ('LINEBELOW', (0, 0), (-1, 0), 0.20, colors.blue),
                ('ALIGN', (0, 0), (-1, 1), 'CENTER')
            ]))
        store.append(resume)
        doc.build(store)
        return response

    @classmethod
    def export_as_csv(cls, request, context):
        stream = StringIO.StringIO()
        csv_writer = csv.writer(stream)
        csv_writer.writerow(settings.EXPORT_CSV_COLUMNS)
        csv_writer.writerows(cls.make_rows(context))
        response = HttpResponse(stream.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0:s}"'.format(cls.get_filename(context, 'csv'))
        return response

    # noinspection DjangoOrm
    def post(self, request, *args, **kwargs):
        context = {
            'form': forms.CompanyForm(self.post_changed(request)),
            'form_step': 1
        }
        context.update(csrf(request))
        if context['form'].is_valid():
            company = models.Company.objects.get(pk=request.POST['name'])

            context['form_step'] = 2
            context_changed = context['form'].cleaned_data['context_changed']

            if int(request.POST['form_step']) == context['form_step'] and not context_changed:
                context['related_form'] = forms.ContractForm(request.POST, params={
                    'contracts': company.contract_set.filter(archive=False)
                })

                if context['related_form'].is_valid():
                    contract = models.Contract.objects.get(pk=request.POST['contracts'])

                    context['period_form'] = forms.PeriodForm(request.POST, params={
                        'period': contract.period_set,
                    })

                    if context['period_form'].is_valid():
                        periods = context['period_form'].cleaned_data['period']
                        periods = periods if len(periods) > 0 else contract.period_set.all()
                        context.update(self.extra_context(request, contract, periods))
            else:
                context['related_form'] = forms.ContractForm(params={
                    'contracts': company.contract_set.filter(archive=False)
                })
        if '_export_as' in request.POST and request.POST['_export_as']:
            return getattr(self, 'export_as_' + request.POST['_export_as'])(request, context)

        return render(request, "contracts/contracts.html", context)

    @staticmethod
    def extra_context(request, contract, periods):
        tickets = remotesyc.models.Ticket.objects.filter(organization_id=contract.company.organization_external)

        if not request.POST['status'] == remotesyc.models.Ticket.STATUS.ALL:
            tickets = tickets.filter(status=request.POST['status'])

        extra_context = {
            'contract': contract,
            'intervals': {}
        }
        for period in periods:
            extra_context['intervals'][period] = tickets.filter(updated_at__range=[period.dt_start, period.dt_end])

        # horas do total de tickets nos períodos selecionados
        extra_context['spent_hours'] = utils.calc_spent_hours(contract, extra_context['intervals'].values())

        if len(periods) == 1:
            spent_credits = utils.calc_spent_credits(contract, periods[0], request.POST['status'])

            # total de horas válidas
            extra_context['valid_hours'] = contract.average_hours + spent_credits

            # saldo devedor
            extra_context['spent_credits'] = spent_credits

            extra_context['remainder_hours'] = extra_context['valid_hours'] - extra_context['spent_hours']
        else:
            extra_context['remainder_hours'] = utils.calc_remainder_hours(contract, extra_context['spent_hours'])

        return extra_context