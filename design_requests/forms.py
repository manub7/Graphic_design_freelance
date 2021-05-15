from django import forms

from orders.models import Order, Category

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('category','name','width','height', 'description')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        


