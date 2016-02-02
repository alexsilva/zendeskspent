# coding=utf-8
from django.core.context_processors import csrf
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from reportlab.lib.styles import getSampleStyleSheet
from export import report_as_pdf, report_as_csv, get_filename

import datetime
import copy
import forms
import models
import remotesyc.models
import utils


styleSheet = getSampleStyleSheet()


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

    @classmethod
    def export_as_pdf(cls, context):
        contract = context['contract']
        intervals = context['intervals']
        spent_hours = context['spent_hours']
        remainder_hours = context['remainder_hours']

        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{0!s}"'.format(
            get_filename(contract.company.name, 'pdf')
        )
        response.write(report_as_pdf(contract, intervals, spent_hours, remainder_hours))

        return response

    @classmethod
    def export_as_csv(cls, context):
        contract = context['contract']
        intervals = context['intervals']
        spent_hours = context['spent_hours']
        remainder_hours = context['remainder_hours']

        # Create the HttpResponse object with the appropriate CSV headers.
        response = HttpResponse(
            report_as_csv(contract, intervals, spent_hours, remainder_hours),
            content_type='text/csv'
        )
        response['Content-Disposition'] = 'attachment; filename="{0:s}"'.format(
            get_filename(contract.company.name, 'csv')
        )

        return response

    # noinspection DjangoOrm
    def post(self, request):
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
            return getattr(self, 'export_as_' + request.POST['_export_as'])(context)

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
            extra_context['intervals'][period] = tickets.filter(created_at__range=[period.dt_start, period.dt_end])

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
