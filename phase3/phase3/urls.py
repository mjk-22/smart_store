"""
URL configuration for phase3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('testing', views.testing, name="testing"),
    path('admin/', admin.site.urls),

    path("", views.dashboard, name="dashboard"),  # homepage
    path("api/fridges/latest/", views.api_latest_readings, name="api_latest_readings"),
    path("fridge/<int:pk>/thresholds/", views.update_thresholds, name="update_thresholds"),
    path("store/", views.store_view, name="store"),  # client form
    # path("fridge/<int:pk>/fan/", views.fan_toggle, name="fan_toggle"),
]
