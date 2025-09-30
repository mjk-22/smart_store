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
        # fname = (request.POST.get("fname") or "").strp()
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

# Create your views here.
# from django.http import HttpResponse, HttpResponseNotAllowed
# from django.shortcuts import render
# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse, HttpResponseNotAllowed
# from django.shortcuts import render

# def store_view(request):
#     if request.method == "GET":
#         return render(request, 'smartstore/store.html')
    
#     elif request.method == "POST":
#         fname = request.POST.get("fname")
#         lname = request.POST.get("lname")

#         if fname: #checks if the variable exists and is not null
#             return render(request, 'smartstore/store.html')
        
#         if lname: #checks if the variable exists and is not null
#             return render(request, 'smartstore/store.html')
        
#         try:
#             return -1 #These returns are just placeholders
#             # Try to insert the fields into the database here
#         except:
#             # If an exception is thrown when inserting, insert logic for lights and buzzers here
#             return -1
#         else:   #If no errors were raised, which means the sql is successful, this block is reached
#             return -1         
#             #insert code here for turning the blue light on
            
#     else:
#         return HttpResponseNotAllowed(["GET"])