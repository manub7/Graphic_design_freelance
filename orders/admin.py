from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Order, Category

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    
    
    list_display = (
        'client',
        'order_number',
        'date',
        'name',
        'category',
        'size',
        'price',
        'processed_image',
        'is_processed'
    )

    ordering = ('category',)

class OrderCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(Category, OrderCategoryAdmin)
