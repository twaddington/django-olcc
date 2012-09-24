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

    # humans.txt
    (r'^humans\.txt$', direct_to_template,
        {'template': 'humans.txt', 'mimetype': 'text/plain'}),

    # robots.txt
    (r'^robots\.txt$', direct_to_template,
        {'template': 'robots.txt', 'mimetype': 'text/plain'}),

    # crossdomain.xml
    (r'^crossdomain\.xml$', direct_to_template,
        {'template': 'crossdomain.xml', 'mimetype': 'application/xml'}),
)

# Static files
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
else:
    urlpatterns += patterns('',
        (r'^static/(?P.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}),
    )
