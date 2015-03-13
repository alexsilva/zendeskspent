from django.conf.urls import patterns, url


urlpatterns = patterns('remotesyc.views',
    url(r'sync/', 'sync', name='remotesync'),
)
