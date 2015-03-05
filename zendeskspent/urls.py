from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

urlpatterns = patterns('',
                       
    url(r'^admin/', include(xadmin.site.urls)),
)
