from django.shortcuts import render, redirect
from .models import Customers, Products, InventoryReceived, Receipts, Receipts_Products
from .forms import CustomerForm, ProductForm, InventoryForm
from django.db import transaction
from django.utils import timezone


def default(request):
    if (request.method == "POST"):
        if ("create_customer" in request.POST):
            customer_form = CustomerForm(request.POST)
            if customer_form.is_valid():
                customer_form.save()
                return redirect("")
        elif ("create_product" in request.POST):
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product_form.save()
                return redirect("")
        elif ("add_inventory" in request.POST):
            inventory_form = InventoryForm(request.POST)
            if inventory_form.is_valid():
                inventory = inventory_form.save()
                inventory.product.stock_quantity += inventory.quantity_received
                inventory.product.save()
                return redirect("")
        elif ("checkout" in request.POST):
            return redirect("")
        
    else:
        customer_form = CustomerForm()
        product_form = ProductForm()
        inventory_form = InventoryForm()

    customers = Customers.objects.all()
    products = Products.objects.all()
    receipts = Receipts.objects.all()
    inventory = InventoryReceived.objects.all()

    context = {
        'customer_form': customer_form,
        'product_form': product_form,
        'inventory_form': inventory_form,
        'customers': customers,
        'products': products,
        'receipts': receipts,
        'inventory': inventory,
    }

    if (request.method == "GET"):
        return render(request, "index.html")