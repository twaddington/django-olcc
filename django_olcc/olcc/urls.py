from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('olcc.views',
    url(r'', 'home', name='home'),
    url(r'^p/(?P<page>\d+)/$', 'product_list', name='product_list'),
    url(r'^p/(?P<slug>[-\w]+)/$', 'product_detail', name='product_detail'),
)
