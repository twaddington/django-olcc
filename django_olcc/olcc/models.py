import re

from django.db import models, IntegrityError
from django.db.models import F
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

def format_phone(phone):
    """
    Sanitize an input string and format the result as a
    phone number.
    """
    phone = re.sub(r'[^0-9]', '', phone)
    return "(%s) %s-%s" % (phone[:3], phone[3:6], phone[6:])

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
    slug = models.SlugField(unique=True, max_length=50,)
    title = models.CharField(max_length=200, db_index=True,)

    status = models.CharField(blank=True, default="", max_length=200)
    description = models.TextField(blank=True, default="",)
    size = models.CharField(blank=True, max_length=10, default="",
            help_text="Bottle size",)
    bottles_per_case = models.PositiveIntegerField(blank=True, default=0)
    proof = models.DecimalField(blank=True, max_digits=5, decimal_places=2,
            default=0)
    age = models.DecimalField(blank=True, max_digits=5, decimal_places=2,
            default=0, help_text="Age in years",)

    current_price = models.ForeignKey('ProductPrice', related_name='+', unique=False,
            blank=True, null=True, help_text="The current price for this Product.",)
    previous_price = models.ForeignKey('ProductPrice', related_name='+', unique=False,
            blank=True, null=True, help_text="The most recently active price for this Product.",)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = ProductManager()

    def save(self, *args, **kwargs):
        # Sanitize the title
        self.title = self.format_title(self.title)

        # Create a slug
        if not self.slug:
            self.slug = slugify(self.code)

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
    def format_title(cls, title):
        """
        Format the product title.
        """
        return " ".join([word.capitalize() for word in title.split()])

    @classmethod
    def is_code_valid(cls, code):
        """
        Validate a product code.
        :return: A regular expression Match object if valid; otherwise None.
        """
        return re.match(r'\d{4,5}\w', code)


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
    key = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    address = models.CharField(max_length=200,)
    address_raw = models.CharField(max_length=200,)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
            blank=True, default=0, db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
            blank=True, default=0, db_index=True)
    county = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=14,)
    hours_raw = models.CharField(max_length=200,)

    def __unicode__(self):
        return u'[%s] %s' % (self.key, self.address,)

    @classmethod
    def from_row(cls, values):
        """
        Create a new Store object from a row of OLCC store data.
        """
        # key, name, phone, address, hours, county
        store = None
        store_key = values[0]
        if store_key:
            try:
                # Update an existing store record
                store = Store.objects.get(key=store_key)
            except Store.DoesNotExist, IntegrityError:
                # Create new store
                store = Store()
                store.key = int(store_key)

            # Update model
            store.name = "%s Liquor" % values[1].strip()
            store.phone = format_phone(values[2].strip())
            store.address = values[3].strip()
            store.address_raw = store.address
            store.hours_raw = values[4].strip()
            store.county = values[5].strip()
            store.save()

        return store
