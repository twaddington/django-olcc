import datetime

from django.db import models, IntegrityError
from django.db.models import F
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

class ProductImport(models.Model):
    """
    This model represents a product import.
    """
    url = models.CharField(max_length=255, db_index=True)
    etag = models.CharField(max_length=32,
            help_text="The value of the ETag header returned from the server.")
    local_checksum = models.CharField(max_length=32,
            help_text="The local md5 hexdigest of the file.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

class ProductManager(models.Manager):
    def on_sale(self):
        """
        Find products whose current_price amount is less than their previous_price amount.
        """
        return self.get_query_set().filter(current_price__amount__lt=F('previous_price__amount'))

class Product(models.Model):
    """
    This model represents a product.

    :todo: Determine a better way to group products, where a product can have
    multiple sizes and prices per size.
    """
    code = models.CharField(unique=True, max_length=200)
    status = models.CharField(blank=True, default="", max_length=200)
    title = models.CharField(max_length=200, db_index=True,)
    slug = models.SlugField(unique=True, max_length=50,)
    description = models.TextField(blank=True, default="",
            help_text="",)
    size = models.CharField(max_length=10,
            help_text="",)
    bottles_per_case = models.PositiveIntegerField()

    current_price = models.ForeignKey('ProductPrice', related_name='+', unique=False,
            blank=True, null=True, help_text="The current price for this Product.",)
    previous_price = models.ForeignKey('ProductPrice', related_name='+', unique=False,
            blank=True, null=True, help_text="The most recently active price for this Product.",)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = ProductManager()

    def save(self, *args, **kwargs):
        # Sanitize the title
        self.title = self.title.strip()

        # Create a slug
        if not self.slug:
            self.slug = slugify("%s %s" % (self.title, self.code,))

        super(Product, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{title} ({size})'.format(title=self.title, size=self.size,)

    def get_absolute_url(self):
        pass

    @property
    def price(self):
        """
        Return the current price of the Product.
        """
        return self.current_price

    @classmethod
    def from_row(cls, values):
        """
        Create a new Product with a row of data from
        an OLCC price document.

        :todo: Effective date for historical price data?
        """
        product = None
        product_code = values[0]
        if product_code:
            try:
                # Update an existing product
                product = Product.objects.get(code=product_code)
            except Product.DoesNotExist, IntegrityError:
                # Create new product
                product = Product()
                product.code = product_code

            # Set product properties
            product.status = values[1]
            product.title = cls.format_title(values[2])
            product.size = values[3]
            product.bottles_per_case = values[4]
            product.save()

            # Get the effective date for the product price
            today = datetime.date.today()
            try:
                next_month = today.replace(month=today.month+1, day=1)
            except ValueError:
                if today.month == 12:
                    next_month = today.replace(year=today.year+1, month=1, day=1)

            # Move the current_price to the previous_price
            try:
                product.previous_price = product.current_price
            except ProductPrice.DoesNotExist:
                pass

            # Add the product price
            product.current_price = ProductPrice.objects.create(amount=str(values[5]),
                    effective_date=next_month, product=product)
            product.save()

        return product

    @classmethod
    def format_title(cls, title):
        """
        Format the product title.
        """
        return " ".join([word.capitalize() for word in title.split()])

class ProductImage(models.Model):
    """
    This model represents a product image.
    """
    url = models.CharField(max_length=200,)
    created_at = models.DateTimeField(auto_now_add=True,)
    modified_at = models.DateTimeField(auto_now=True,)
    product = models.ForeignKey(Product)

class ProductPrice(models.Model):
    """
    This model represents a historical product price.
    """
    amount = models.DecimalField(max_digits=9, decimal_places=2, db_index=True,)
    effective_date = models.DateField(db_index=True,)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,)
    modified_at = models.DateTimeField(auto_now=True, db_index=True,)
    product = models.ForeignKey(Product, unique=False, related_name="prices")

    class Meta:
        unique_together = ("product", "effective_date")

    def __unicode__(self):
        return u'%d' % (self.amount,)

class Store(models.Model):
    """
    This model represents the physical location of an
    OLCC run liquor store.

    :todo: Parse hours into a machine readable format.
    :todo: Write a from_row method.
    """
    key = models.IntegerField(db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    address = models.CharField(max_length=200,)
    address_raw = models.CharField(max_length=200,)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
            db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
            db_index=True)
    county = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=10,)
    hours_raw = models.CharField(max_length=200,)

    def __unicode__(self):
        return u'%s' % (self.name,)
