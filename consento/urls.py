from django.contrib import admin
from django.conf.urls import patterns, include, url


# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()


# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^v1/venues/search$', 'apps.consento_api.views.venue_search'),
    url(r'^v1/venues/home$', 'apps.consento_api.views.venue_home'),
    url(r'^v1/venues/keyword$', 'apps.consento_api.views.venue_keyword'),
    url(r'^v1/venues/(?P<venue_id>\d+)$', 'apps.consento_api.views.venue_detail'),
)