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

class SalesReportsFiltersForm(forms.Form):
    start_date = forms.DateField(required = False, widget = forms.DateInput(attrs= {"type" : "date"}))
    end_date = forms.DateField(required = False, widget = forms.DateInput(attrs={"type" : "date"}))
    category = forms.ChoiceField(required = False, choices = [("","All Categories")], widget=forms.Select())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Products.objects.values_list("category", flat=True).distinct()
        self.fields["category"].choices += [(c, c) for c in categories]

class DateRangeForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class PurchaseSearchForm(forms.Form):
    item_name = forms.CharField(max_length=255)
