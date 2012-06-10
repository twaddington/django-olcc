from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from olcc.models import Product, ProductPrice, Store

def home_view(request):
    """
    The site landing page.
    """
    context = {}
    return render_to_response('olcc/home.html',
            context, context_instance=RequestContext(request))

def product_list_view(request, page=1):
    """
    Display a paginated list of products.
    """
    per_page = int(request.GET.get('pp', 25))
    products = Product.objects.all().order_by('title')

    p = Paginator(products, per_page)
    try:
        products_page = p.page(page)
    except InvalidPage:
        raise Http404
    
    context = {
        'products_page': products_page, 
    }

    return render_to_response('olcc/product_list.html',
            context, context_instance=RequestContext(request))

def sale_list_view(request, page=1):
    """
    Display a paginated list of on sale products.
    """
    per_page = int(request.GET.get('pp', 25))
    products = Product.objects.on_sale().order_by('title')

    p = Paginator(products, per_page)
    try:
        products_page = p.page(page)
    except InvalidPage:
        raise Http404
    
    context = {
        'products_page': products_page, 
    }

    return render_to_response('olcc/product_list.html',
            context, context_instance=RequestContext(request))

def product_view(request, slug):
    """
    Display product details.
    """
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        raise Http404

    context = {
        'product': product,
    }

    return render_to_response('olcc/product.html',
            context, context_instance=RequestContext(request))

def store_list_view(request):
    """
    Display a list of stores.
    """
    # Order by county, then name
    stores = Store.objects.all().order_by('county', 'name')[:5]

    context = {
        'stores': stores,
    }

    return render_to_response('olcc/stores.html',
            context, context_instance=RequestContext(request))

