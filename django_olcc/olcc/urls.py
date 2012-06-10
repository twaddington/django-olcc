from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('olcc.views',
    url(r'^$', 'home_view', name='home'),
    
    # Products
    url(r'^products/(?P<page>\d+)/$', 'product_list_view', name='products'),
    url(r'^products/$', 'product_list_view', name='products'),
    url(r'^products/(?P<slug>[-\w]+)/$', 'product_view', name='product'),

    # Sale
    url(r'^sale/(?P<page>\d+)/$', 'product_list_view',
            kwargs={'sale': True,}, name='sale'),
    url(r'^sale/$', 'product_list_view', kwargs={'sale': True,}, name='sale'),

    # Stores
    url(r'^stores/$', 'store_view', name='stores'),
    url(r'^stores/(?P<county>\w+)/$', 'store_list_view'),

    # Static about page
    url(r'^about/$', direct_to_template,
            {'template': 'olcc/about.html',}, name='about'),
)
