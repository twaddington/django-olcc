from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('olcc.views',
    url(r'^$', 'home', name='home'),
    url(r'^p/(?P<page>\d+)/$', 'product_list', name='products'),
    url(r'^(?P<slug>[-\w]+)/$', 'product_detail', name='product'),
    url(r'^s/(?P<page>\d+)/$', 'store_list', name='stores'),
)
