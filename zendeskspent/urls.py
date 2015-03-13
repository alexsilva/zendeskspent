from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

urlpatterns = patterns('',
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),
    url(r'^remote/', include("remotesyc.urls")),
    url(r'^admin/', include(xadmin.site.urls)),
    url(r'^$', include("contracts.urls")),
)
