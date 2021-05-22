from django import forms
from orders.widgets import CustomClearableFileInput
from .models import DesignRequest, Category
from orders.models import Order
from profiles.models import Client


class OrderFormDesignRequest(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = (
            'category',
            'name',
            'height',
            'width',
            'description',
            'provide_source_files',
            'source_img',
            'is_processed',
            'processed_image',
            'testimonial',
            )


    source_img = forms.ImageField(label='attachments', required=False, widget=CustomClearableFileInput)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category = Category.objects.filter(name=self.fields['category'])
        self.fields['category'] = category
        

        super().__init__(*args, **kwargs)
        placeholders = {
            'category':'Category',
            'name':'Design Request Name',
            'description': 'Design Request Description',
            'height':'height',
            'width':'width',
            'provide_source_files':'Provide Source Files?',
            'source_img':'Source Image',
            'is_processed': 'Is Processed',
            'processed_image': 'Processed Image',
            'testimonial':"Your testimonial",
            
        }
        
        self.fields['category'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False


class OrderFormDesignRequestSuser(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = (
            'category',
            'name',
            'height',
            'width',
            'description',
            'provide_source_files',
            'source_img',
            'is_processed',
            'processed_image',
            'testimonial',
            )
    
    source_img = forms.ImageField(label='source_img', required=False, widget=CustomClearableFileInput),
    processed_image = forms.ImageField(label='processed_image', required=False, widget=CustomClearableFileInput),

  

    def __init__(self, *args, **kwargs):
        super(OrderFormDesignRequestSuser,self).__init__(*args, **kwargs)
        self.fields['processed_image'] =  forms.ImageField(label='processed_image', required=False, widget=CustomClearableFileInput),

        

        super(OrderFormDesignRequestSuser,self).__init__(*args, **kwargs)
        placeholders = {
            'category':'Category',
            'name':'Design Request Name',
            'description': 'Design Request Description',
            'height':'height',
            'width':'width',
            'provide_source_files':'Provide Source Files?',
            'source_img':'Source Image',
            'is_processed': 'Is Processed',
            'processed_image': 'Processed Image',
            'testimonial':"Your testimonial",
            
        }
        
        self.fields['category'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False


class OrderFormCheckOut(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'street_address1',
            'street_address2',
            'town_or_city',
            'county',
            'postcode',
            'country',
            )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        self.fields['first_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country' :
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False
