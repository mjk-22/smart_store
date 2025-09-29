from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render

def store_view(request):
    if request.method == "GET":
        return render(request, 'smartstore/store.html')
    
    elif request.method == "POST":
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")

        if fname: #checks if the variable exists and is not null
            return render(request, 'smartstore/store.html')
        
        if lname: #checks if the variable exists and is not null
            return render(request, 'smartstore/store.html')
        
        try:
            return -1 #These returns are just placeholders
            # Try to insert the fields into the database here
        except:
            # If an exception is thrown when inserting, insert logic for lights and buzzers here
            return -1
        else:   #If no errors were raised, which means the sql is successful, this block is reached
            return -1         
            #insert code here for turning the blue light on
            
    else:
        return HttpResponseNotAllowed(["GET"])
    