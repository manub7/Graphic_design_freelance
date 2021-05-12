from django.db import models
from django.conf import settings

# Create your models here.

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name
def product_path (instance,filename):
    return 'media/'.format(filename)

class Product(models.Model):

    category = models.ForeignKey('Category', null =True, blank=True, on_delete=models.SET_NULL  )
    sku = models.CharField(max_length=254,null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    height = models.DecimalField(max_digits = 6, decimal_places=0)
    width = models.DecimalField(max_digits = 6, decimal_places=0)
    size = models.DecimalField(max_digits = 6, decimal_places=0)
    price = models.DecimalField(max_digits = 6, decimal_places=2)
    image_url = models.URLField(max_length = 1024, null = True, blank = True)
    image = models.ImageField(null=True, blank=True)
    

    def __str__(self):
        return self.name
    
    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    @classmethod
    def create(self, data, files):
        category = Category.objects.filter(id=data['category']).get()


        product = Product(
            
            category = category,
            description=data['description'],
            width=data['width'],
            height=data['height'],
            size = data['width'] * data['height'] *3 /1024,
            price = size * settings.PRICE_FACTOR,
            provide_source_files=True if 'provide_source_files' in data else False,
            is_processed=False,

        )
        product.save()
    
