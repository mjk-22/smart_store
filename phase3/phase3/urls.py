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
    path('', views.default, name='default'),
    path('admin/', admin.site.urls),

    # API endpoints for dashboard JS
    path("fridges/latest/", views.get_latest_readings, name="fridge_latest"),
    path("fridges/<int:pk>/thresholds/", views.update_thresholds, name="fridge_thresholds"),
    path("fridges/<int:pk>/fan-toggle/", views.fan_toggle, name="fridge_fan_toggle"),

   
    # Product management system
    path('product-management/', views.product_management_home, name='product_management'),
    path('customers/create/', views.create_customer_page, name='create_customer_page'),
    path('products/create/', views.create_product_page, name='create_product_page'),
    path('inventory/add/', views.add_inventory_page, name='add_inventory_page'),
    path('customers/', views.customers_page, name='customers_page'),
    path('products/', views.products_page, name='products_page'),
    path('inventory/', views.inventory_page, name='inventory_page'),
    path('receipts/', views.receipts_page, name='receipts_page'),
    path('receipts/<int:receipt_id>/', views.receipt_admin_detail, name='receipt_admin_detail'),

    # Self-checkout system
    path('self-checkout/', views.self_checkout_home, name='self_checkout_home'),
    path('self-checkout/login/', views.self_checkout_login, name='self_checkout_login'),
    path('self-checkout/cart/', views.self_checkout_cart, name='self_checkout_cart'),
    path('account/', views.customer_account, name='customer_account'),
    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    path('checkout/', views.checkout, name='checkout_api'),
     path("self-checkout/logout/", views.checkout_logout, name="checkout_logout"),
]