from django.urls import path
from .views import store_view
# from django.contrib import admin

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", store_view, name="store"),
    # 
]