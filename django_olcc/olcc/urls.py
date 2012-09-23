from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import direct_to_template

from tastypie.api import Api
from olcc.api import ProductResource, ProductPriceResource, StoreResource

v1_api = Api(api_name='v1')
v1_api.register(ProductResource())
v1_api.register(ProductPriceResource())
v1_api.register(StoreResource())

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
    url(r'^stores/(?P<county>[\w\s]+)/$', 'store_view'),
    url(r'^stores/$', 'store_view', name='stores'),

    # REST API
    (r'^api/', include(v1_api.urls)),
)
