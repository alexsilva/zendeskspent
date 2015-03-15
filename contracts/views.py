from django.core.context_processors import csrf
from django.shortcuts import render
from django.views.generic import View

import forms
import models
import remotesyc.models


class ContractView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "contracts/contracts.html", {
            'form': forms.CompanyForm(),
            'form_step': 1
        })

    def post(self, request, *args, **kwargs):
        context = {
            'form': forms.CompanyForm(request.POST),
            'form_step': 1
        }
        context.update(csrf(request))

        if context['form'].is_valid():
            company = models.Company.objects.get(pk=request.POST['name'])

            context['form_step'] = 2

            if int(request.POST['form_step']) == context['form_step']:
                context['related_form'] = forms.ContractForm(request.POST, params={
                    'contracts': company.contract_set
                })

                if context['related_form'].is_valid():
                    contract = models.Contract.objects.get(pk=request.POST['contracts'])

                    context['period_form'] = forms.PeriodForm(request.POST, params={
                        'period': contract.period_set,
                    })

                    if context['period_form'].is_valid():
                        context['data'] = self.do_filter(request, contract, context['period_form'].cleaned_data['period'])
                        context['contract'] = contract
            else:
                context['related_form'] = forms.ContractForm(params={
                    'contracts': company.contract_set
                })
        return render(request, "contracts/contracts.html", context)

    def do_filter(self, request, contract, periods):
        tickets = remotesyc.models.Ticket.objects.filter(organization_id=contract.company.organization_external)

        if not request.POST['status'] == remotesyc.models.Ticket.STATUS.ALL:
            tickets = tickets.filter(status=request.POST['status'])

        related = {}
        periods = periods if len(periods) > 0 else contract.period_set.all()

        for period in periods:
            related[period] = tickets.filter(updated_at__range=[period.dt_start, period.dt_end])
        return related