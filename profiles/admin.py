from django.contrib import admin
from .models import Client

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    
    
    list_display = (
    'user',
    'default_phone_number',
    'default_street_address1' ,
    'default_street_address2' ,
    'default_town_or_city' ,
    'default_county' ,
    'default_postcode',
    'default_country',
    )

    ordering = ('category',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )


admin.site.register(Client, ProfileAdmin)

