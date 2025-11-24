from django.db import models
from django.core.validators import *
import uuid

class Customers(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(unique=True, max_length=15, blank=True, validators=[RegexValidator(regex=r'^\d{9,15}$')])
    password = models.CharField(null=False)
    membership_id = models.UUIDField(default=uuid.uuid1, editable=False)
    points = models.PositiveIntegerField(default=0, null=False) 

class Receipts(models.Model):
    customer_id = models.ForeignKey(Customers, on_delete=models.CASCADE)
    time = models.DateTimeField()
    points_earned = models.IntegerField(default=0)
    total_price = models.IntegerField()

class Products(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.FloatField()
    epc = models.CharField(max_length=50, unique=True)
    upc = models.CharField(max_length=50, unique=True)
    producer_company = models.CharField(max_length=100)
    image_url = models.CharField()
    stock_quantity = models.IntegerField(default=0)
    expiry_date = models.DateField()
    def __str__(self):
        return self.name

class Receipts_Products(models.Model):
    receipt_id = models.ForeignKey(Receipts, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    product_quantity = models.IntegerField()

    class Meta:
        unique_together = ('receipt_id', 'product_id')
        db_table = 'receipts_products'

class InventoryReceived(models.Model):
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    date_received = models.DateField()
    quantity_received = models.IntegerField()

class Fridge(models.Model):
    name = models.CharField(max_length=50)
    topic = models.CharField(max_length=100)
    temperature = models.FloatField(default=0)
    humidity = models.FloatField(default=0)
    temp_threshold = models.FloatField(default=0)
    humidity_threshold = models.FloatField(default=0)
    fan_on = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name