# models.py
from django.db import models

class Clothes(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='clothes_images')  # Add image field

    def __str__(self):
        return self.name

class KeyChain(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='keychain_images')  # Add image field

    def __str__(self):
        return self.name

class Wallet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='wallet_images')  # Add image field

    def __str__(self):
        return self.name

from django.db import models
import json

class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default=None)
    payment = models.CharField(max_length=100)
    total_price_after_gst = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.TextField(default='[]')  # Default value set to an empty list

    def __str__(self):
        return f'Order #{self.id}'

    def set_products(self, products):
        self.products = json.dumps(products)

    def get_products(self):
        return json.loads(self.products)
