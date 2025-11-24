from django import forms
from .models import Customers, Products, InventoryReceived

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customers
        fields = ['name', 'email', 'phone_number', 'password']
        widgets = {
            'password': forms.PasswordInput(),  # hide password
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'category', 'price', 'epc', 'upc',
                  'producer_company', 'expiry_date']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryReceived
        fields = ['product_id', 'date_received', 'quantity_received']

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())