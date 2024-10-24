from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    url_name = models.SlugField(unique=True, default='none')  # Specify a default value
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # Add image field

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

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
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f'Order #{self.id}'

    def set_products(self, products):
        self.products = json.dumps(products)

    def get_products(self):
        return json.loads(self.products)

