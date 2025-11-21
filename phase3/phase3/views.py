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
    

def create_customer_page(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("create_customer_page")
    else:
        form = CustomerForm()

    context = {"form": form}
    return render(request, "create_customer.html", context)


def create_product_page(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("create_product_page")
    else:
        form = ProductForm()

    context = {"form": form}
    return render(request, "create_product.html", context)


def add_inventory_page(request):
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            inventory = form.save(commit=False)
            product = inventory.product_id        
            product.stock_quantity += inventory.quantity_received
            product.save()
            inventory.save()
            return redirect("add_inventory_page")
    else:
        form = InventoryForm()

    context = {"form": form}
    return render(request, "add_inventory.html", context)

def customers_page(request):
    if request.method == "POST" and "delete_customer" in request.POST:
        customer_id = request.POST.get("delete_customer")
        Customers.objects.filter(id=customer_id).delete()
        return redirect("customers_page")

    customers = Customers.objects.all()
    context = {"customers": customers}
    return render(request, "customers.html", context)


def products_page(request):
    if request.method == "POST" and "delete_product" in request.POST:
        product_id = request.POST.get("delete_product")
        Products.objects.filter(id=product_id).delete()
        return redirect("products_page")

    products = Products.objects.all()
    context = {"products": products}
    return render(request, "products.html", context)


def inventory_page(request):
    inventory = InventoryReceived.objects.all()
    context = {"inventory": inventory}
    return render(request, "inventory.html", context)


def receipts_page(request):
    receipts = Receipts.objects.all()
    context = {"receipts": receipts}
    return render(request, "receipts.html", context)

def checkout(request):
    if request.method != "POST" or request.headers.get("Content-Type") != "application/json":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
        if data.get("action") != "checkout":
            return JsonResponse({"success": False, "error": "Unsupported action"}, status=400)

        cart = data.get("cart", {})
        if not cart:
            return JsonResponse({"success": False, "error": "Cart is empty"}, status=400)

        # TODO: get the real logged-in customer
        customer = Customers.objects.get(id=1)

        total_price = 0

        with transaction.atomic():
            #update products and does total
            for product_id, item in cart.items():
                product = Products.objects.get(id=product_id)
                quantity = int(item["quantity"])

                product.stock_quantity -= quantity
                product.save()

                total_price += float(product.price) * quantity

            #create receipt
            receipt = Receipts.objects.create(
                customer_id=customer,
                time=timezone.now(),
                points_earned=int(total_price // 10), 
                total_price=total_price,
            )

            for product_id, item in cart.items():
                product = Products.objects.get(id=product_id)
                quantity = int(item["quantity"])
                Receipts_Products.objects.create(
                    receipt_id=receipt,
                    product_id=product,
                    product_quantity=quantity,
                )

        return JsonResponse({"success": True, "redirect_url": "/receipts/"})
    except Exception as e:
        print("Checkout error:", e)
        return JsonResponse({"success": False, "error": "Checkout failed"}, status=500)

