import uuid
from django.db import models
from profiles.models import Client
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
    testimonial = models.TextField(null =True, blank=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    street_address1 = models.CharField(max_length=80, null=True, blank=True)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    country = CountryField(blank_label='Country', null=True, blank=True)
    upload = models.FileField(upload_to=order_directory_path, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def upload_attachments(cls, files, design_request):
        for file in files:
            filename = 'media/' + str(design_request.id)

            with open(filename, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        return None

    @classmethod
    def create(self,data,files,client):
        category = Category.objects.filter(id=data['category']).get()
        design_request = Order (
            client=client,
            category=category,
            name=data['name'],
            description=data.get('description'),
            width=data['width'],
            height=data['height'],
            provide_source_files=True if 'provide_source_files' in data else False,
            source_img= image,
            is_processed=False,
            first_name = data['first_name'],
            last_name = data['last_name'],
            phone_number = data['phone_number'],
            street_address1 = data.get('street_adress1'),
            street_address2 = data.get('street_adress2'),
            town_or_city = data['town_or_city'],
            county = data['county'],
            postcode = data['postcode'],
            country = data['country'],
        )
        design_request.save()




    @classmethod
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
        self.size = int(self.width) * int(self.height) * 3 / 1024
        self.price = int(self.size) * settings.PRICE_FACTOR / 1000

        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.order_number
    