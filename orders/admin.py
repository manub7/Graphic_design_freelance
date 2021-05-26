from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Order

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    
    
    list_display = (
        'design_request',
        'price',
        'order_number',
        'date',
        'client',
        
    )

    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)

