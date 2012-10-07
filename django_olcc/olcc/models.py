import datetime
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

class ImportRecord(models.Model):
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

    class Meta:
        get_latest_by = 'created_at'

class ProductManager(models.Manager):
    def on_sale(self):
        """
        Find all products that have dropped in price since last month.
        """
        return self.get_query_set().filter(on_sale=True)

class Product(models.Model):
    """
    This model represents a product.

    :todo: Determine a better way to group products, where a product can have
           multiple sizes and prices per size.
    """
    code = models.CharField(unique=True, max_length=200)
    slug = models.SlugField(unique=True, max_length=50,)
    title = models.CharField(max_length=200, db_index=True,)
    on_sale = models.BooleanField(default=False, db_index=True,)

    status = models.CharField(blank=True, default="", max_length=200)
    description = models.TextField(blank=True, default="",)
    size = models.CharField(blank=True, max_length=10, default="",
            help_text="Bottle size",)
    bottles_per_case = models.PositiveIntegerField(blank=True, default=0)
    proof = models.DecimalField(blank=True, max_digits=5, decimal_places=2,
            default=0)
    age = models.DecimalField(blank=True, max_digits=5, decimal_places=2,
            default=0, help_text="Age in years",)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = ProductManager()

    class Meta:
        ordering = ['title',]

    def save(self, *args, **kwargs):
        # Sanitize the title
        self.title = self.format_title(self.title)

        # Create a slug
        if not self.slug:
            self.slug = slugify(self.code)

        super(Product, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{title} ({size})'.format(title=self.title, size=self.size,)

    @models.permalink
    def get_absolute_url(self):
        return ('olcc.views.product_view', (), {'slug': self.slug})

    @property
    def price(self):
        """
        Return the current price for this Product.
        """
        today = datetime.date.today()
        this_month = today.replace(day=1)

        return self.prices.get(effective_date=this_month)

    @property
    def previous_price(self):
        """
        Return last month's price for this Product.
        """
        today = datetime.date.today()

        # Get the first of last month
        try:
            last_month = today.replace(month=today.month-1, day=1)
        except ValueError:
            if today.month == 1:
                last_month = today.replace(year=today.year-1, month=12, day=1)

        return self.prices.get(effective_date=last_month)

    @property
    def next_price(self):
        """
        Return last month's price for this Product.
        """
        today = datetime.date.today()

        # Get the first of next month
        try:
            next_month = today.replace(month=today.month+1, day=1)
        except ValueError:
            if today.month == 12:
                next_month = today.replace(year=today.year+1, month=1, day=1)

        return self.prices.get(effective_date=next_month)

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
    product = models.ForeignKey(Product, related_name='images')

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
        ordering = ['-effective_date',]
        get_latest_by = 'effective_date'

    def __unicode__(self):
        return u'$%.2f' % (self.amount,)

class Store(models.Model):
    """
    This model represents the physical location of an
    OLCC run liquor store.
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

    class Meta:
        ordering = ['county', 'name',]

    def __unicode__(self):
        return u'[%s] %s' % (self.key, self.address,)

    def tel(self):
        """
        Return the phone number as an RFC 3966 formatted string.
        """
        p = re.sub(r'[^0-9]', '', self.phone)
        return "+1-%s-%s-%s" % (p[:3], p[3:6], p[6:])

    @property
    def hours_list(self):
        return [h.strip() for h in self.hours_raw.split(';')]

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
