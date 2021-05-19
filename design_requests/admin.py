from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DesignRequest, Category

# Register your models here.
class DesignRequestAdmin(admin.ModelAdmin):
    
    
    list_display = (
        'id',
        'name',
        'category',
        'size',
        'price',
        'processed_image',
        'source_img',
        'is_processed'
    )

    ordering = ('category',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )

admin.site.register(DesignRequest, DesignRequestAdmin)
admin.site.register(Category, CategoryAdmin)