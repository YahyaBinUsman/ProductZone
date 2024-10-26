from django.db import models
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist

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
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)  # New field for discounted items
    is_best_seller = models.BooleanField(default=False)  # New field for best sellers
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def discounted_price(self):
        """Calculates a 15% discounted price if the product is marked as discounted."""
        if self.is_discounted:
            return self.price * Decimal('0.85')  # 15% discount
        return self.price
    
    def save(self, *args, **kwargs):
        if self.is_discounted:
            if not self.original_price:
                self.original_price = self.price
            # Convert 0.85 to a Decimal
            self.price = round(self.original_price * Decimal('0.85'), 2)
        else:
            if self.original_price:
                self.price = self.original_price
                self.original_price = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
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
    updated_at = models.DateTimeField(auto_now=True)  # Track last update time
    products = models.TextField(default='[]')  # JSON of products
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f'Order #{self.id}'

    def set_products(self, products):
        self.products = json.dumps(products)

    def get_products(self):
        try:
            products_data = json.loads(self.products)
            product_list = []

            for item in products_data:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)

                try:
                    product = Product.objects.get(id=product_id)
                    product_list.append({
                        "name": product.name,
                        "image_url": product.image.url if product.image else "",
                        "quantity": quantity,
                        "price": product.price,
                        "tax": product.price * Decimal('0.18'),
                        "total_price_with_tax": (product.price + product.price * Decimal('0.18')) * quantity
                    })
                except ObjectDoesNotExist:
                    continue

            return product_list

        except json.JSONDecodeError:
            return []

    def parsed_products(self):
        product_list = []
        products_str = self.products
        for item in products_str.split(','):
            if '(' in item and ')' in item:
                name = item.split('(')[0].strip()
                quantity = int(item.split('(')[1].replace(')', '').strip())
                try:
                    product = Product.objects.get(name=name)
                    product_list.append({'id': product.id, 'name': name, 'quantity': quantity})
                except Product.DoesNotExist:
                    continue
        return product_list  # Return after the loop completes