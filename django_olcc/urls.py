from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template

# Enable the django admin
admin.autodiscover()

urlpatterns = patterns('',
    # Wire up olcc urls
    url(r'', include('olcc.urls')),

    # Wire up the admin urls
    url(r'^admin/', include(admin.site.urls)),

    # Static files
    #(r'^static/(?P<static>.*)$', 'django.views.static.serve',
    #    {'document_root': settings.STATIC_ROOT}),

    # robots.txt
    (r'^robots\.txt$', direct_to_template,
        {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)

# Static files
urlpatterns += staticfiles_urlpatterns()
