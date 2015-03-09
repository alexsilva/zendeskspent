from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

urlpatterns = patterns('',
    url(r'^remote/', include("remotesyc.urls")),
    url(r'^admin/', include(xadmin.site.urls)),
    url(r'^contracts/', include("contracts.urls")),
)
