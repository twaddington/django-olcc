from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('olcc.views',
    url(r'^products/(?P<page>\d+)/$', 'product_list'),
    url(r'^product/(?P<slug>[-\w]+)/$', 'product_detail'),
)
