from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client
from .light import show_success,show_failure
from django.http import HttpResponseNotAllowed

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
