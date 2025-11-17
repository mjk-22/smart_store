from django.shortcuts import render, redirect
from .models import Customers, Products, InventoryReceived, Receipts, Receipts_Products
from .forms import CustomerForm, ProductForm, InventoryForm
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
import json


def default(request):
    customer_form = CustomerForm()
    product_form = ProductForm()
    inventory_form = InventoryForm()
    customers = Customers.objects.all()
    products = Products.objects.all()
    receipts = Receipts.objects.all()
    inventory = InventoryReceived.objects.all()

    if (request.method == "POST"):
        if ("create_customer" in request.POST):
            customer_form = CustomerForm(request.POST)
            if customer_form.is_valid():
                customer_form.save()
            return redirect("default")
        elif ("delete_customer" in request.POST):
            customer_id = request.POST.get("delete_customer")
            Customers.objects.filter(id=customer_id).delete()
            return redirect("default")
        elif ("create_product" in request.POST):
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product_form.save()
            return redirect("default")
        elif ("delete_product" in request.POST):
            product_id = request.POST.get("delete_product")
            Products.objects.filter(id=product_id).delete()
            return redirect("default")
        elif ("code_add" in request.POST):
            product_epc = request.POST.get("code_search")
            return Products.objects.filter(epc=product_epc)
        elif ("add_inventory" in request.POST):
            inventory_form = InventoryForm(request.POST)
            if inventory_form.is_valid():
                inventory = inventory_form.save()
                inventory.product_id.stock_quantity += inventory.quantity_received
                inventory.product_id.save()
            return redirect("default")
        elif (request.headers.get("Content-Type") == "application/json"):
            try:
                data = json.loads(request.body.decode("utf-8"))
                if (data.get("action") == "checkout"):
                    cart = data.get("cart", {})
                    print(cart)

                    # Since everything is done on the dashboard, I haven't implemented a login
                    # feature yet, so there isn't a customer ID that gets passed through yet
                    #
                    # customer_id = data.get("customer_id")
                    # customer = Customers.objects.get(id=customer_id)
                    customer = Customers.objects.get(id=1)
                    total_price = 0

                    with transaction.atomic():
                        for product_id, item_data in cart.items():
                            quantity = item_data["quantity"]
                            product= Products.objects.get(id=product_id)
                            product.stock_quantity -= quantity
                            product.save()
                            total_price += product.price * quantity
                        
                        receipt = Receipts.objects.create(
                            customer_id = customer,
                            time=timezone.now(),
                            points_earned = int(total_price // 10),
                            total_price=total_price
                        )

                        for product_id, item_data in cart.items():
                            item_quantity = item_data["quantity"]
                            item_product = Products.objects.get(id=product_id)
                            Receipts_Products.objects.create(
                                receipt_id = receipt,
                                product_id = item_product,
                                product_quantity = item_quantity
                            )


                    return JsonResponse({"success": True, "redirect_url": "/"})
            except Exception as e:
                return JsonResponse({"success": False, "redirect_url": "/"})                 
        else:
            return redirect("default")

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
        return render(request, "index.html", context=context)