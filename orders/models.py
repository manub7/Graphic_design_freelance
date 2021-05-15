import uuid
from django.db import models
from profiles.models import Client
from django.conf import settings
from decimal import *

# Create your models here.

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name


def product_path (instance,filename):
    return 'media/'.format(filename)


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders')
    order_number = models.CharField(max_length=32, null=False, editable=False)
    date = models.DateTimeField(auto_now_add=True)
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
    testimonial = models.TextField(default=False,null = False)

    def __str__(self):
        return self.name
    
    def create(self,data,files,client):
        

        design_request = Order (
            client=client,
            category=category,
            description=data['description'],
            width=data['width'],
            height=data['height'],
            provide_source_files=True if 'provide_source_files' in data else False,
            is_processed=False

        )
        design_request.save()
        self.upload_attachements(file,design_request)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        self.size =self.width * self.height * 3 / 1024
        self.price = self.size * settings.PRICE_FACTOR / 1000

        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.order_number
    