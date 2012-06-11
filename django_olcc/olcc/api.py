from tastypie import fields
from tastypie.resources import ModelResource, ALL
from olcc.models import Product, ProductPrice, Store

class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'
        allowed_methods = ['get']
        filtering = {
            'title': ALL,
            'code': ALL,
            'proof': ALL,
            'size': ALL,
            'status': ALL,
            'on_sale': ALL,
        }

class ProductPriceResource(ModelResource):
    product = fields.ToOneField(ProductResource, 'product')

    class Meta:
        queryset = ProductPrice.objects.all()
        resource_name = 'price'
        allowed_methods = ['get']
        filtering = {
            'product': ['exact'],
        }

class StoreResource(ModelResource):
    class Meta:
        queryset = Store.objects.all()
        resource_name = 'store'
        allowed_methods = ['get']
