from django.db import models

class Model(models.Model):
    """
    """
    item_code = models.CharField(unique=True, max_length=200,)
    item_status = models.CharField(blank=True, default="", max_length=200,)
    title = models.CharField(max_length=200, db_index=True,)
    slug = models.SlugField(max_length=50, db_index=True,)
    description = models.TextField(blank=True, default="",
            help_text="",)
    size = models.CharField(max_length=10,
            help_text="",)
    bottles_per_case = models.PositiveIntegerField()
    prices = models.ManyToManyField(ModelPrice)
    image = models.ForeignKey(ModelImage)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    @property
    def price(self):
        pass

    def get_absolute_url(self):
        pass

    def __unicode__(self):
        return u'{title} ({size})'.format(title=self.title, size=self.size,)

    def save(self, *args, **kwargs):
        super(Model, self).save(*args, **kwargs)

class ModelPrice(models.Model):
    """
    """
    amount = models.DecimalField(max_digits=5, decimal_places=2, db_index=True,)
    effective_date = models.DateField(db_index=True,)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,)
    modified_at = models.DateTimeField(auto_now=True, db_index=True,)


class ModelImage(models.Model):
    """
    """
    url = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
