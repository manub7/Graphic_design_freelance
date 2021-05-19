import uuid
from django.db import models
from django.conf import settings
from decimal import *
from django_countries.fields import CountryField

# Create your models here.

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name


def order_directory_path (instance,filename):
    return 'media/'.format(filename)


class DesignRequest(models.Model):

    category = models.ForeignKey('Category', null =True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    description = models.TextField()
    height = models.DecimalField(max_digits = 6, decimal_places=0)
    width = models.DecimalField(max_digits = 6, decimal_places=0)
    size = models.DecimalField(max_digits = 13, decimal_places=0, editable=False, null = False, default=0 )
    price = models.DecimalField(max_digits = 13, decimal_places=2, editable=False, null = False, default=0 )
    provide_source_files = models.BooleanField(default=False)
    source_img = models.ImageField(null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    processed_image = models.ImageField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    testimonial = models.TextField(null =True, blank=True)



    def __int__(self):
        return self.id


    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        self.size = int(self.width) * int(self.height) * 3 / 1024
        self.price = int(self.size) * settings.PRICE_FACTOR / 1000

        super().save(*args, **kwargs)

    