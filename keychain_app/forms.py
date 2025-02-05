from django import forms
from .models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description','url_name','image']

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'gross_price', 'quantity', 'image',
            'is_featured', 'is_discounted', 'is_best_seller', 'category', 'rack_number',
            'barcode'  # ✅ Include barcode in the form
        ]
       
