from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from olcc.forms import CountyForm
from olcc.models import Product, ProductPrice, Store

def home_view(request):
    """
    The site landing page.
    """
    # Get a random set of on sale products to highlight
    on_sale = Product.objects.all().order_by('?')[:5]

    # Get a random set of products to highlight, excluding
    # any on sale items we are already showing.
    products = Product.objects.all().exclude(
            pk__in=[p.pk for p in on_sale]).order_by('?')[:5]

    context = {
        'on_sale': on_sale,
        'products': products,
    }
    return render_to_response('olcc/home.html',
            context, context_instance=RequestContext(request))

def product_list_view(request, page=1, sale=False):
    """
    Display a paginated list of products.
    """
    per_page = int(request.GET.get('pp', 25))

    if sale:
        title = 'On Sale'
        products = Product.objects.on_sale()
    else:
        title = 'Products'
        products = Product.objects.all()

    # Order the product list
    products = products.order_by('title')

    p = Paginator(products, per_page)
    try:
        products_page = p.page(page)
    except InvalidPage:
        raise Http404
    
    context = {
        'title': title,
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

def store_view(request, county=None):
    """
    Display a form for filtering a list of stores by county.
    """
    stores = None

    if request.method == 'POST':
        form = CountyForm(request.POST)
        if form.is_valid():
            return redirect(store_view, county=form.cleaned_data['county'])

    if county:
        stores = Store.objects.filter(county__iexact=county)

        # Order by county, then name
        stores = stores.order_by('county', 'name')

        # Build our form
        form = CountyForm({'county': county})
    else:
        form = CountyForm()

    context = {
        'form': form,
        'county': county.title(),
        'stores': stores,
    }

    return render_to_response('olcc/store_list.html',
            context, context_instance=RequestContext(request))
