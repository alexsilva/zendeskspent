from django.core.context_processors import csrf
from django.shortcuts import render
from django.views.generic import View

import forms
import models


class ContractView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "contracts/contracts.html", {
            'form': forms.CompanyForm(),
            'form_step': 1
        })

    def post(self, request, *args, **kwargs):
        params = {
            'form': forms.CompanyForm(request.POST),
            'form_step': 1
        }
        params.update(csrf(request))

        if params['form'].is_valid():
            company = models.Company.objects.get(pk=request.POST['name'])

            params['form_step'] = 2

            if int(request.POST['form_step']) == params['form_step']:
                params['related_form'] = forms.ContractForm(request.POST, params={
                    'contracts': company.contract_set
                })

                if params['related_form'].is_valid():
                    contract = models.Contract.objects.get(pk=request.POST['contracts'])

                    params['period_form'] = forms.PeriodForm(request.POST, params={
                        'period': contract.period_set,
                    })
                    self.do_filter()
            else:
                params['related_form'] = forms.ContractForm(params={
                    'contracts': company.contract_set
                })
        return render(request, "contracts/contracts.html", params)

    def do_filter(self):
        pass
