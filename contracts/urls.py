from django.conf.urls import patterns, url
from contracts import views

__author__ = 'alex'


urlpatterns = patterns('contracts.views',
    url(r'', views.ContractView.as_view(), name='contracts-form'),
)
