# coding=utf-8
from django import forms
import remotesyc.models
import models


__author__ = 'alex'


class CompanyForm(forms.ModelForm):
    status = forms.ChoiceField(label="Estado", choices=remotesyc.models.Ticket.STATUS.CHOICES)

    name = forms.ModelChoiceField(queryset=models.Company.objects.all(),
                                  empty_label='Selecione uma empresa',
                                  label='Empresas',
                                  required=True)

    class Meta:
        model = models.Company
        fields = ('status', 'name')


class ContractForm(forms.Form):
    contracts = forms.ModelChoiceField(queryset=models.Contract.objects.none(),
                                       empty_label=u'Selecione uma opção de contrato',
                                       label="Contratos",
                                       required=True)

    def __init__(self, *args, **kwargs):
        params = kwargs.pop('params', {})

        super(ContractForm, self).__init__(*args, **kwargs)

        self.fields['contracts'].queryset = params.get('contracts', models.Contract.objects.none())


class PeriodForm(forms.Form):
    period = forms.ModelMultipleChoiceField(queryset=models.Period.objects.none(), label="Datas",
                                            required=False)

    def __init__(self, *args, **kwargs):
        params = kwargs.pop('params', {})

        super(PeriodForm, self).__init__(*args, **kwargs)

        self.fields['period'].queryset = params.get('period', models.Period.objects.none())