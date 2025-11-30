from django.shortcuts import render, redirect
from .models import Customers, Products, InventoryReceived, Receipts, Receipts_Products
from .forms import CustomerForm, ProductForm, InventoryForm, LoginForm, SalesReportsFiltersForm,DateRangeForm,PurchaseSearchForm
from django.db import transaction
from django.db.models import Sum, F, Q, Value, FloatField, Min, Count
from django.db.models.functions import Coalesce 
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from .models import Fridge
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from datetime import date

def default(request):
    # this *is* your fridge dashboard now
    fridges = Fridge.objects.order_by("id")
    fridges_data = list(
        fridges.values(
            "id",
            "name",
            "topic",
            "temperature",
            "humidity",
            "temp_threshold",
            "humidity_threshold",
            "fan_on",
            "updated_at",
        )
    )
    context = {
        "fridges": fridges,
        "fridges_data": fridges_data,
    }
    return render(request, "dashboard.html", context)


def get_latest_readings(request):
    fridges = list(
        Fridge.objects.values(
            "id",
            "name",
            "topic",
            "temperature",
            "humidity",
            "temp_threshold",
            "humidity_threshold",
            "fan_on",
            "updated_at",
        ).order_by("id")
    )
    return JsonResponse({"fridges": fridges})


@csrf_exempt
def update_thresholds(request, pk):
    fridge = get_object_or_404(Fridge, pk=pk)
    if request.method == "POST":
        try:
            t = request.POST.get("temp_threshold")
            h = request.POST.get("humidity_threshold")

            if t is not None:
                fridge.temp_threshold = float(t)
            if h is not None:
                fridge.humidity_threshold = float(h)

            fridge.save(update_fields=["temp_threshold", "humidity_threshold"])
            messages.success(request, f"{fridge.name} thresholds updated.")
        except Exception as e:
            messages.error(request, f"Failed to update thresholds: {e}")
    return redirect("default")


@require_POST
def fan_toggle(request, pk):
    fridge = get_object_or_404(Fridge, pk=pk)
    action = (request.POST.get("action") or "").upper()
    want_on = (action == "ON")

    fridge.fan_on = want_on
    fridge.save(update_fields=["fan_on"])

    try:
        import paho.mqtt.publish as publish
        hostname = "localhost"
        topic = f"fan/{fridge.topic}/cmd"
        payload = action
        publish.single(topic, payload, hostname=hostname)
    except Exception:
        pass

    return redirect("default")
    

def create_customer_page(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer=form.save()
            messages.success(request,f"Customer '{customer.name}' was created.")

            return redirect("create_customer_page")
    else:
        form = CustomerForm()

    context = {"form": form}
    return render(request, "create_customer.html", context)


def create_product_page(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product=form.save()
            messages.success(request,f"Product '{product.name}' was created.")

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
            messages.success(request,f"Added '{inventory.quantity_received}' units to '{product.name}'.")
            return redirect("add_inventory_page")
    else:
        form = InventoryForm()

    context = {"form": form}
    return render(request, "add_inventory.html", context)

def customers_page(request):
    if request.method == "POST" and "delete_customer" in request.POST:
        customer_id = request.POST.get("delete_customer")
        Customers.objects.filter(id=customer_id).delete()
        messages.success(request,f"Customer deleted")
        return redirect("customers_page")

    customers = Customers.objects.all()
    context = {"customers": customers}
    return render(request, "customers.html", context)


def products_page(request):
    if request.method == "POST" and "delete_product" in request.POST:
        product_id = request.POST.get("delete_product")
        Products.objects.filter(id=product_id).delete()
        messages.success(request,f"Product deleted")
        return redirect("products_page")

    products = Products.objects.all()
    context = {"products": products}
    return render(request, "products.html", context)


def inventory_page(request):
    inventory = InventoryReceived.objects.all()
    context = {"inventory": inventory}
    return render(request, "inventory.html", context)


def receipts_page(request):
    receipts = Receipts.objects.select_related("customer_id").all().order_by("-time")
    context = {"receipts": receipts}
    return render(request, "receipts.html", context)

def receipt_admin_detail(request, receipt_id):
    receipt = get_object_or_404(Receipts, id=receipt_id)
    items = Receipts_Products.objects.filter(
        receipt_id=receipt
    ).select_related("product_id")

    context = {
        "receipt": receipt,
        "items": items,
    }
    return render(request, "receipt_admin_detail.html", context)

def checkout(request):
    if request.method != "POST" or request.headers.get("Content-Type") != "application/json":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    customer_id = request.session.get("customer_id")
    if not customer_id:
        return JsonResponse({"success": False, "error": "Not logged in"}, status=403)

    try:
        data = json.loads(request.body.decode("utf-8"))
        if data.get("action") != "checkout":
            return JsonResponse({"success": False, "error": "Unsupported action"}, status=400)

        cart = data.get("cart", {})
        if not cart:
            return JsonResponse({"success": False, "error": "Cart is empty"}, status=400)

        customer = Customers.objects.get(id=customer_id)
        total_price = 0

        with transaction.atomic():
            for product_id, item in cart.items():
                product = Products.objects.get(id=product_id)
                quantity = int(item["quantity"])

                product.stock_quantity -= quantity
                product.save()

                total_price += float(product.price) * quantity

            points_earned = int(total_price // 10)
            receipt = Receipts.objects.create(
                customer_id=customer,
                time=timezone.now(),
                points_earned=points_earned,
                total_price=total_price,
            )

            customer.points += points_earned
            customer.save(update_fields=["points"])

            for product_id, item in cart.items():
                product = Products.objects.get(id=product_id)
                quantity = int(item["quantity"])
                Receipts_Products.objects.create(
                    receipt_id=receipt,
                    product_id=product,
                    product_quantity=quantity,
                )

        return JsonResponse({
            "success": True,
            "redirect_url": f"/receipt/{receipt.id}/"
        })
    except Exception as e:
        print("Checkout error:", e)
        return JsonResponse({"success": False, "error": "Checkout failed"}, status=500)
    

def product_management_home(request):
    return render(request, "product_management.html")

def self_checkout_home(request):
    return render(request, "self_checkout_home.html")

def self_checkout_login(request):
    login_form = LoginForm()
    register_form = CustomerForm()

    if request.method == "POST":
        if "login" in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data["email"]
                password = login_form.cleaned_data["password"]
                customer = Customers.objects.filter(email=email, password=password).first()
                if customer:
                    request.session["customer_id"] = customer.id
                    return redirect("self_checkout_cart")
                else:
                    login_form.add_error(None, "Invalid email or password.")
        elif "register" in request.POST:
            register_form = CustomerForm(request.POST)
            if register_form.is_valid():
                customer = register_form.save()
                request.session["customer_id"] = customer.id
                return redirect("self_checkout_cart")

    context = {
        "login_form": login_form,
        "register_form": register_form,
    }
    return render(request, "self_checkout_login.html", context)

def checkout_logout(request):
    logout(request)
    return redirect('self_checkout_home')   


def self_checkout_cart(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("self_checkout_login")

    customer = get_object_or_404(Customers, id=customer_id)
    products = Products.objects.all().order_by("name")
    receipts = Receipts.objects.filter(customer_id=customer).order_by("-time")

    context = {
        "customer": customer,
        "products": products,
        "receipts": receipts,
    }
    return render(request, "self_checkout_cart.html", context)


def customer_account(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("self_checkout_login")

    customer = get_object_or_404(Customers, id=customer_id)
    receipts = Receipts.objects.filter(customer_id=customer).order_by("-time")

    context = {"customer": customer, "receipts": receipts}
    return render(request, "customer_account.html", context)


def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(Receipts, id=receipt_id)
    items = Receipts_Products.objects.filter(receipt_id=receipt).select_related("product_id")
    context = {
        "receipt": receipt,
        "items": items,
        "customer": receipt.customer_id,
    }
    return render(request, "receipt_detail.html", context)

def admin_reports_home(request):
    return render(request, "admin_reports_home.html")


def sales_report(request):
    form = SalesReportsFiltersForm(request.GET or None)

    start_date = form["start_date"].value() or "2025-11-01"
    end_date = form["end_date"].value() or str(date.today())
    category = form["category"].value() or ""
    products = Products.objects.all()

    highest_selling = None
    lowest_selling = None
    date_filter = {}

    start_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date) 

    if category:
        products = products.filter(category=category)

    date_filter = {
        "receipts_products__receipt_id__time__date__gte":start_date,
        "receipts_products__receipt_id__time__date__lte":end_date
    }

    products_with_sales = products.annotate(
        quantity_sold=Coalesce(
            Sum("receipts_products__product_quantity", filter=Q(**date_filter)),
            Value(0)
        ),
        revenue=Coalesce(
            Sum(
                F("receipts_products__product_quantity") * F("price"),
                filter=Q(**date_filter),
            ),
            Value(0.0)
        )
    ).order_by("name")

    total_revenue = sum(p.revenue for p in products_with_sales)

    if (products_with_sales):
        max_quantity = max(p.quantity_sold for p in products_with_sales)
        min_quantity = min(p.quantity_sold for p in products_with_sales)

        highest_selling = [p for p in products_with_sales if p.quantity_sold == max_quantity]
        lowest_selling = [p for p in products_with_sales if p.quantity_sold == min_quantity]
    else:
        highest_selling = []
        lowest_selling = []
        max_quantity = 0
        min_quantity = 0

    context = {
        "form": form,
        "products": products_with_sales,
        "highest_selling": highest_selling,
        "lowest_selling": lowest_selling,
        "highest_quantity": max_quantity,
        "lowest_quantity": min_quantity,
        "total_revenue": total_revenue,
        "start_date": start_date,
        "end_date": end_date
    }

    return render(request, "sales_report.html", context)


def inventory_report(request):

    form = SalesReportsFiltersForm(request.GET or None)

    start_date_str = form["start_date"].value() or "2025-11-01"
    end_date_str   = form["end_date"].value() or str(date.today())
    category       = form["category"].value() or ""

    start_date = date.fromisoformat(start_date_str)
    end_date   = date.fromisoformat(end_date_str)

    products = Products.objects.all()
    if category:
        products = products.filter(category=category)

    date_filter = Q(
        inventoryreceived__date_received__gte=start_date,
        inventoryreceived__date_received__lte=end_date,
    )

    products_with_inventory = (
        products.annotate(
            quantity_received=Coalesce(
                Sum(
                    "inventoryreceived__quantity_received",
                    filter=date_filter,
                ),
                Value(0),
            )
        )
        .order_by("name")
    )

    context = {
        "form": form,
        "products": products_with_inventory,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "inventory_report.html", context)

def activity_report(request):

    form = SalesReportsFiltersForm(request.GET or None)

    start_date_str = form["start_date"].value() or "2025-11-01"
    end_date_str = form["end_date"].value() or str(date.today())

    start_date = date.fromisoformat(start_date_str)
    end_date = date.fromisoformat(end_date_str)

    receipts = Receipts.objects.filter(
        time__date__gte=start_date,
        time__date__lte=end_date
    )

    total_customers = receipts.values("customer_id").distinct().count()

 
    new_customers = (
        Customers.objects.annotate(new_customer=Min("receipts__time"))
        .filter(new_customer__date__gte=start_date,new_customer__date__lte=end_date)
        .count()
    )

    returning_customers = max(total_customers - new_customers, 0)

    context = {
        "form": form,
        "start_date": start_date,
        "end_date": end_date,
        "total_customers": total_customers,
        "new_customers": new_customers,
        "returning_customers": returning_customers,
    }

    return render(request, "activity_report.html", context)


# This allows the customer to check their receipt history and their total money spent and theri search in purchase history
def customer_receipt_history(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("self_checkout_login")

    customer = get_object_or_404(Customers, id=customer_id)

    # --- Date Range Filter ---
    receipts = Receipts.objects.filter(customer_id=customer).order_by("-time")
    form = DateRangeForm(request.GET)

    if form.is_valid():
        start = form.cleaned_data.get("start_date")
        end = form.cleaned_data.get("end_date")
        if start:
            receipts = receipts.filter(time__date__gte=start)
        if end:
            receipts = receipts.filter(time__date__lte=end)

    total_spent = receipts.aggregate(sum=Sum("total_price"))["sum"] or 0

    # --- Item Search Filter ---
    search_form = PurchaseSearchForm(request.GET)
    info = None

    if "item_name" in request.GET and search_form.is_valid():
        name = search_form.cleaned_data["item_name"]

        items = Receipts_Products.objects.filter(
            receipt_id__customer_id=customer,
            product_id__name__icontains=name
        ).select_related("product_id", "receipt_id").order_by("-receipt_id__time")

        info = {
            "item_name": name,
            "count": items.count(),
            "items": items,
        }

    return render(request, "customer_receipt_history.html", {
        "customer": customer,
        "receipts": receipts,
        "form": form,
        "search_form": search_form,
        "info": info,
        "total_spent": total_spent,
    })
