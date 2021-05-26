import uuid
from django.db import models
from profiles.models import Client
from django.conf import settings
from decimal import *
from design_requests.models import DesignRequest
from profiles.models import Client
from django_countries.fields import CountryField


def order_directory_path (instance,filename):
    return 'media/'.format(filename)

class Order(models.Model):
    
    design_request = models.ForeignKey(DesignRequest,on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='design_request', editable = False)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders')
    price = models.DecimalField(max_digits = 13, decimal_places=2, editable=False, null = False, default=0 )
    order_number = models.CharField(max_length=32, null=False, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    street_address1 = models.CharField(max_length=80, null=True, blank=True)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    country = CountryField(blank_label='Country', null=True, blank=True)
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')


    def __str__(self):
        return self.name

   
    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        Overide the original save method to set the order number
        if it hasn't been set already.
        """

        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.order_number
    