from tastypie.resources import ModelResource
from olcc.models import Product, ProductPrice, Store

class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'

class ProductPriceResource(ModelResource):
    class Meta:
        queryset = ProductPrice.objects.all()
        resource_name = 'price'

class StoreResource(ModelResource):
    class Meta:
        queryset = Store.objects.all()
        resource_name = 'store'
