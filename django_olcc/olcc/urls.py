from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('olcc.views',
    url(r'^$', 'home_view', name='home'),
    url(r'^stores/$', 'store_list_view', name='stores'),
    url(r'^products/(?P<page>\d+)/$', 'product_list_view', name='products'),
    url(r'^sale/(?P<page>\d+)/$', 'sale_list_view', name='sale'),
    url(r'^p/(?P<slug>[-\w]+)/$', 'product_view', name='product'),

    # Static about page
    url(r'^about/$', direct_to_template,
        {'template': 'olcc/about.html',}, name='about'),
)
