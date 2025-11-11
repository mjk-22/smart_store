from .models import Customers, Products, InventoryReceived, Receipts, Receipts_Products
from .forms import CustomerForm, ProductForm, InventoryForm
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
import json

from django.contrib import messages
from .models import Client
from .light import show_success,show_failure
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from .models import Fridge
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import serial
from serial.tools import list_ports
import time

def testing(request):
    customer_form = CustomerForm()
    product_form = ProductForm()
    inventory_form = InventoryForm()
    customers = Customers.objects.all()
    products = Products.objects.all()
    receipts = Receipts.objects.all()
    inventory = InventoryReceived.objects.all()

    # ports = list_ports.comports()
    # for port in ports:
    #     print(f"Device: {port.device}, Description: {port.description}, HWID: {port.hwid}")
    
    # try:
    #     ser = serial.Serial("/dev/ttyAMA10", 9600, timeout=1)
    #     print(f"Connected to {'/dev/ttyAMA10'}")

    #     while True:
    #         # Read data from the serial port
    #         serial_data = ser.readline()
    #         if serial_data:
    #             try:
    #                 tag_id = serial_data.decode('utf-8').strip()
    #                 if tag_id:
    #                     print(f"Tag ID: {tag_id}")
    #             except UnicodeDecodeError:
    #                 print("Could not decode data to UTF-8")
    #         time.sleep(0.1)
    # except serial.SerialException as e:
    #     print(f"Serial port error: {e}")
    # except KeyboardInterrupt:
    #     print("Exiting Program")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    # finally:
    #     if 'ser' in locals() and ser.is_open:
    #         ser.close()
    #         print("Serial port closed.")


    if (request.method == "POST"):
        if ("create_customer" in request.POST):
            customer_form = CustomerForm(request.POST)
            if customer_form.is_valid():
                customer_form.save()
            return redirect("testing")
        elif ("delete_customer" in request.POST):
            customer_id = request.POST.get("delete_customer")
            Customers.objects.filter(id=customer_id).delete()
            return redirect("testing")
        elif ("create_product" in request.POST):
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product_form.save()
            return redirect("testing")
        elif ("delete_product" in request.POST):
            product_id = request.POST.get("delete_product")
            Products.objects.filter(id=product_id).delete()
            return redirect("testing")
        elif ("add_inventory" in request.POST):
            inventory_form = InventoryForm(request.POST)
            if inventory_form.is_valid():
                inventory = inventory_form.save()
                inventory.product_id.stock_quantity += inventory.quantity_received
                inventory.product_id.save()
            return redirect("testing")
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
            return redirect("testing")

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
    
# phase1 client
def store_view(request):
    if request.method == "GET":
        return render(request, 'smartstore/store.html')
    
    if request.method == "POST":
        print("POST received:",request.POST)
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if not fname or not lname:
            show_failure()
            messages.error(request, "First and Last name are required.")
            return render(request, "smartstore/store.html",{"data":request.POST})

        try:
            Client.objects.create(first_name=fname,last_name=lname,email=email or None,phone=phone or "",)
        except Exception as e:
            show_failure()
            messages.error(request, f"Could not save client: {e}")
            return render(request, "smartstore/store.html",{"data":request.POST})
        print("saving client & calling show_success()")
        show_success()
        messages.success(request, "Client added successfuly.")
        return redirect("store")
    
    return HttpResponseNotAllowed(["GET","POST"])


# phase 2 fridge
def dashboard(request):
    fridges = Fridge.objects.order_by("id")
    fridges_data = list(fridges.values(
            "id","name","topic","temperature","humidity",
            "temp_threshold","humidity_threshold","updated_at"
        )
    )
    return render(request, "smartstore/dashboard.html", {
        "fridges": fridges,              
        "fridges_data": fridges_data,    
    })


def api_latest_readings(request):
    fridges = list(
        Fridge.objects.values(
            "id", "name", "topic",
            "temperature", "humidity",
            "temp_threshold", "humidity_threshold", "fan_on",
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
    return redirect("dashboard")


@require_POST
def fan_toggle(request, pk):
    f = get_object_or_404(Fridge, pk=pk)
    action = (request.POST.get("action") or "").upper() 
    want_on = (action == "ON")
    # update DB
    f.fan_on = want_on
    f.save(update_fields=["fan_on"])
    messages.success(request, f"Fan for {f.name} set to {action}.")

    # publish an MQTT command so fan_control.py acts
    try:
        import paho.mqtt.publish as publish
        publish.single(f"fan/{f.topic}/cmd", action, hostname="localhost", port=1883)
    except Exception:
        pass

    return redirect("dashboard")