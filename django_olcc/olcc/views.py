from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from olcc.models import Product

def product_list(request, page=1):
    """
    Display a paginated list of products.
    """
    per_page = int(request.GET.get('pp', 25))
    products = Product.objects.all().order_by('title')

    p = Paginator(products, per_page)
    try:
        page_obj = p.page(page)
    except InvalidPage:
        raise Http404
    
    context = {
        'page_obj': page_obj, 
    }

    return render_to_response('olcc/product_list.html',
            context, context_instance=RequestContext(request))

def product_detail(request, slug):
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
