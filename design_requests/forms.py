from django import forms
from .widgets import CustomClearableFileInput
from orders.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('category',
                  'width',
                  'height',
                  'description', 
                  'provide_source_files'
                  )
    upload = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)