from django import forms
from .models import Customers, Products, InventoryReceived

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customers
        fields = ['name', 'email', 'phone_number', 'password']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'category', 'price', 'epc', 'upc', 'producer_company']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryReceived
        fields = ['product_id', 'date_received', 'quantity_received']