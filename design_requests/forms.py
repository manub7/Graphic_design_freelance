from django import forms

from orders.models import Order, Category
from profiles.models import Client

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'category',
            'name',
            'width',
            'height', 
            'description', 
            "provide_source_files",
            )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

        


