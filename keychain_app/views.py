
from django.shortcuts import render, get_object_or_404,redirect
from .models import Category, Product,Order
from .forms import CategoryForm, ProductForm  # Create forms in forms.py
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Max,Q,Sum
from django.contrib import messages
from django.shortcuts import render
from .models import Product, Category
def home(request):
    # Fetch all featured products, discounted products, and best sellers
    featured_products = Product.objects.filter(is_featured=True)
    discounted_products = Product.objects.filter(is_discounted=True)
    best_sellers = Product.objects.filter(is_best_seller=True)
    
    # Fetch all categories (if needed in the template)
    categories = Category.objects.all()

    # Render the home template with simplified context
    return render(request, 'index.html', {
        'featured_products': featured_products,
        'categories': categories,
        'discounted_products': discounted_products,
        'best_sellers': best_sellers,
    })


# View for displaying categories and their products
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def product_redirect(request, category, product_id):
    product = get_object_or_404(Product, id=product_id, category__name=category)
    return render(request, 'product_detail.html', {'product': product})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Compose the email
        subject = f"New message from {name}"
        body = f"Message:\n{message}\n\nFrom: {name}\nEmail: {email}"
        recipient_email = 'yahyabinusman7@gmail.com'

        # Send the email
        try:
            send_mail(subject, body, email, [recipient_email])
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect to the same page or a success page
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
            return redirect('contact')

    return render(request, 'contact.html')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price_before_gst = Decimal(0)
    total_gst = Decimal(0)
    total_price_after_gst = Decimal(0)
    total_quantity = 0

    for product_id, item_data in cart.items():
        quantity = item_data.get('quantity', 0)
        if quantity < 1:
            continue  # Skip items with zero quantity or less

        product = get_object_or_404(Product, pk=product_id)
        gst_rate = Decimal(settings.GST_RATE)
        price_before_gst = Decimal(item_data['price']) / (1 + gst_rate)
        gst_amount = Decimal(item_data['price']) - price_before_gst

        # Calculate totals for each item
        item_total_before_gst = price_before_gst * quantity
        item_gst_total = gst_amount * quantity
        item_total_after_gst = Decimal(item_data['price']) * quantity

        # Update cart totals
        total_price_before_gst += item_total_before_gst
        total_gst += item_gst_total
        total_price_after_gst += item_total_after_gst
        total_quantity += quantity

        # Append item details to cart items
        cart_items.append({
            'id': product_id,
            'name': product.name,
            'price_before_gst': price_before_gst,
            'gst_amount': gst_amount,
            'price': item_data['price'],
            'quantity': quantity,
            'total': item_total_after_gst,
        })

    # Calculate subtotal
    subtotal = total_price_before_gst + total_gst

    # Pass totals to template
    return render(request, 'view_cart.html', {
        'cart_items': cart_items,
        'total_price_before_gst': total_price_before_gst,
        'total_gst': total_gst,
        'total_price_after_gst': total_price_after_gst,
        'total_quantity': total_quantity,
        'subtotal': subtotal,
    })

from decimal import Decimal
def add_product_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get(f'quantity_{product_id}', 1))
        product = get_object_or_404(Product, pk=product_id)

        if quantity > product.quantity:
            messages.error(request, "Quantity entered is greater than available stock.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Get the cart from the session
        cart = request.session.get('cart', {})

        # Update cart with product quantity and price
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += quantity
        else:
            cart[str(product_id)] = {
                'quantity': quantity,
                'price': str(product.price)  # Use the stored price directly
                # Ensure you save the name as well
            }

        # Update the session with the new cart data
        request.session['cart'] = cart
        
        # Update product stock after adding to the cart
        product.quantity -= quantity
        product.save()

        # Update cart items in the session
        request.session['cart_items'] = [
            {
                'id': product_id,
                'name': product.name,  # Ensure correct product name is captured
                'price': str(product.price),
                'quantity': item['quantity'],
                'total': str(Decimal(item['price']) * item['quantity'])
            }
            for product_id, item in cart.items()
            for product in [get_object_or_404(Product, pk=product_id)]  # Fetch product to get the correct name
        ]

        messages.success(request, f"{quantity} {product.name}(s) added to your cart.")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})

        if product_id in cart:
            quantity_in_cart = cart[product_id]['quantity']

            if quantity_in_cart > 0:
                product = get_object_or_404(Product, pk=product_id)
                
                # Increase product stock
                product.quantity += 1
                product.save()

                # Decrement the quantity in the cart
                cart[product_id]['quantity'] -= 1

                # Remove item if quantity falls to zero
                if cart[product_id]['quantity'] <= 0:
                    del cart[product_id]

                request.session['cart'] = cart
                messages.success(request, "Product quantity reduced in your cart.")
            else:
                messages.error(request, "There are no more units of this product in your cart.")
        else:
            messages.error(request, "Product is not in your cart.")

    return redirect('view_cart')

def checkout(request):
    cart_items = request.session.get('cart_items', [])
    total_price = request.session.get('total_price', Decimal(0))

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})
 

def error_page(request):
    return render(request,'error.html')


def order_success(request):
    return render(request, 'order_success.html')


def process_order(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        country = 'Pakistan'  # Set country to Pakistan
        payment = 'Cash on Delivery'  # Set payment method
        cart_items = request.session.get('cart_items', [])
        
        # Calculate total price after GST
        total_price_after_gst = sum(Decimal(item['total']) for item in cart_items)

        try:
            with transaction.atomic():
                # Create the order object
                order = Order.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    postal_code=postal_code,
                    city=city,
                    country=country,
                    payment=payment,
                    total_price_after_gst=total_price_after_gst
                )

                # Extract product names for the order
                products = []
                for item in cart_items:
                    product_id = item['id']
                    product_name = item['name'].split('(')[0].strip()  # Extract product name
                    products.append(f"{product_name} ({item['quantity']})")
                
                order.products = ", ".join(products)
                order.save()

                # Deduct quantity permanently upon successful order processing
                for item in cart_items:
                    product_id = item['id']
                    quantity = item['quantity']
                    product = get_object_or_404(Product, pk=product_id)
                    
                    # Ensure that the quantity to be deducted does not exceed the quantity in the cart
                    if quantity <= product.quantity:
                        product.quantity -= quantity
                        product.save()
                    else:
                        messages.error(request, f"Insufficient stock for {product.name}. Order cannot be processed.")

                # Construct the email content for the owner
                subject_owner = 'New Order Placed on Your Website'
                message_owner = (
                    f"New order details:\n\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n"
                    f"Address: {address}\n"
                    f"Postal Code: {postal_code}\n"
                    f"City: {city}\n\n"
                    f"Ordered Products:\n" + "\n".join(f"- {product}" for product in products) +
                    f"\nTotal Price: Rs.{total_price_after_gst}"
                )

                # Send email notification to the owner
                email_from = settings.EMAIL_HOST_USER
                recipient_list_owner = ['yahyabinusman7@gmail.com']  # Replace with actual recipient email
                send_mail(subject_owner, message_owner, email_from, recipient_list_owner)

                # Construct the email content for the customer
                subject_customer = 'Your Order Confirmation'
                message_customer = (
                    f"Dear {name},\n\n"
                    f"Thank you for your order!\n"
                    f"Here are your order details:\n\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n"
                    f"Address: {address}\n"
                    f"Postal Code: {postal_code}\n"
                    f"City: {city}\n\n"
                    f"Ordered Products:\n" + "\n".join(f"- {product}" for product in products) +
                    f"\nTotal Price: Rs.{total_price_after_gst}\n\n"
                    f"Your order will be delivered soon. Thank you for shopping with us!\n\n"
                    f"Best regards,\nYour Company Name"
                )

                # Send email confirmation to the customer
                recipient_list_customer = [email]
                send_mail(subject_customer, message_customer, email_from, recipient_list_customer)

                # Clear the cart session
                request.session['cart'] = {}
                request.session['cart_items'] = []
                request.session['total_price'] = str(Decimal(0))

        except Exception as e:
            # Log error or handle as needed
            print(e)

        # Return a success response
        return redirect('order_success')
    else:
        # If the request method is not POST, return a bad request response
        return JsonResponse({'error': 'Invalid request method.'}, status=400)


def generate_unique_id():
    # Get the maximum ID from the Product model
    max_id = Product.objects.aggregate(Max('id'))['id__max'] or 0
    return max_id + 1


def search(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        # Fetch products with a name or description matching the query and with quantity > 0
        products = Product.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)) & Q(quantity__gt=0)
        )

        # Check if it's an AJAX request using headers
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            results = [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'price': p.price,
                    'category': p.category.name,  # Assuming category has a 'name' field
                    'image_url': p.image.url if p.image else ''  # Include the product image URL
                } for p in products
            ]
            return JsonResponse({'results': results})

        # For form submissions (when the user presses enter or clicks the search button)
        else:
            context = {
                'query': query,
                'products': products,  # Pass the filtered products to the template
            }
            return render(request, 'search_results.html', context)

    return render(request, 'search_results.html', {'query': query, 'products': []})


def faqs(request):
    return render(request, 'faqs.html')


def terms(request):
    return render(request, 'terms.html')


def category_detail(request, url_name):
    category = get_object_or_404(Category, url_name=url_name)  # Assuming your Category model has a `url_name` field
    products = category.products.all()  # Fetch all products related to this category
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_detail.html', context)  # Render your category detail template














@staff_member_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            form.save()
            return redirect('add_category')  # Redirect to the same page or another one
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

from django.shortcuts import get_object_or_404

@staff_member_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('edit_category', pk=pk)  # Redirect to the same page
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form})

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Ensure to handle file uploads
        if form.is_valid():
            form.save()
            return redirect('add_product')  # Redirect after saving
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@staff_member_required
def products_view(request):
    query = request.GET.get('search')
    
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    return render(request, 'products.html', {'products': products})


@staff_member_required
def delete_product(request, product_id):
    # Retrieve the product using the unified Product model
    product = get_object_or_404(Product, pk=product_id)

    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('products_view')

@staff_member_required
def order_details(request):
    search_query = request.GET.get('search', '')

    # Fetch all orders, applying search filters if necessary
    all_orders = Order.objects.all()
    if search_query:
        all_orders = all_orders.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(postal_code__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(products__icontains=search_query)
        )

    total_orders = all_orders.count()
    pending_orders = all_orders.filter(is_complete=False)
    completed_orders = all_orders.filter(is_complete=True)

    # Calculate total sales and potential sales
    total_sales = sum(order.total_price_after_gst for order in completed_orders)
    potential_sales = sum(order.total_price_after_gst for order in pending_orders)

    return render(request, 'order_details.html', {
        'pending_orders': pending_orders,
        'total_orders': total_orders,
        'total_pending_orders': pending_orders.count(),
        'total_sales': total_sales,
        'potential_sales': potential_sales,
        'search_query': search_query,
    })

@staff_member_required
def mark_order_complete(request, order_id):
    # Fetch the order using order_id
    order = get_object_or_404(Order, id=order_id)

    # Mark the order as complete
    if not order.is_complete:
        order.is_complete = True
        order.save()
        messages.success(request, f"Order #{order.id} marked as complete.")
    else:
        messages.warning(request, f"Order #{order.id} is already marked as complete.")

    return redirect('order_details')


@staff_member_required
def products_overview(request):
    search_query = request.GET.get('search', '').strip()

    # Retrieve all categories with their products
    categories = Category.objects.all()

    # Apply search filter to products if a search query is provided
    if search_query:
        products = Product.objects.filter(name__icontains=search_query)
    else:
        products = Product.objects.all()  # Set to all products if no search query

    # Handle feature, discount, and best-seller toggles
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        try:
            product = Product.objects.get(id=product_id)

            if action == 'feature':
                # Feature toggle logic
                if Product.objects.filter(is_featured=True).count() < 12:
                    product.is_featured = True
                    product.save()
                    messages.success(request, f"{product.name} has been featured.")
                else:
                    messages.error(request, "You can only feature up to 12 products.")
            elif action == 'remove':
                product.is_featured = False
                product.save()
                messages.success(request, f"{product.name} has been unfeatured.")
            elif action == 'discount':
                # Discount toggle logic
                product.is_discounted = True
                product.save()
                messages.success(request, f"{product.name} has been added to discounted items.")
            elif action == 'remove_discount':
                product.is_discounted = False
                product.save()
                messages.success(request, f"{product.name} has been removed from discounted items.")
            elif action == 'best_seller':
                # Best-seller toggle logic
                product.is_best_seller = True
                product.save()
                messages.success(request, f"{product.name} has been added to best sellers.")
            elif action == 'remove_best_seller':
                product.is_best_seller = False
                product.save()
                messages.success(request, f"{product.name} has been removed from best sellers.")
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")

    # Prepare data for each category, including totals
    category_data = []
    for category in categories:
        category_products = category.products.all()
        category_quantity = category_products.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        category_price = category_products.aggregate(total_price=Sum('price'))['total_price'] or 0
        category_data.append({
            'category': category,
            'products': category_products,
            'total_quantity': category_quantity,
            'total_price': category_price,
        })

    # Calculate totals for all products
    total_items = products.count()
    total_quantity = products.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_price_sum = products.aggregate(Sum('price'))['price__sum'] or 0

    return render(request, 'products_overview.html', {
        'categories': category_data,
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_price_sum': total_price_sum,
        'search_query': search_query,
        'filtered_products': products,
    })

@staff_member_required
def edit_product(request, product_id):
    # Retrieve the product
    product = get_object_or_404(Product, pk=product_id)

    # Fetch all categories from the database
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.quantity = request.POST['quantity']

        # Handle file upload for the product image
        if request.FILES.get('image'):
            product.image = request.FILES['image']

        # Update the product's category based on the form selection
        category_id = request.POST.get('category')
        if category_id:
            product.category = Category.objects.get(id=category_id)
        
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('products_view')

    return render(request, 'product_form.html', {
        'product': product,
        'categories': categories  # Pass the categories to the template
    })

from decimal import Decimal
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Order, Product
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from decimal import Decimal
from .models import Order, Product

@staff_member_required
def order_detail_view(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id)
    search_query = request.GET.get('search', '')

    # Initialize variables for totals and cart items
    cart_items = []
    total_price_before_gst = Decimal(0)
    total_gst = Decimal(0)
    total_price_after_gst = Decimal(0)
    total_quantity = 0

    # Parse each product in the order
    for item in order.parsed_products():
        product_id = item['id']
        quantity = item['quantity']

        if quantity < 1:
            continue  # Skip items with zero or negative quantity

        # Retrieve product details
        product = get_object_or_404(Product, pk=product_id)
        gst_rate = Decimal(settings.GST_RATE)

        # Calculate price breakdown
        price_before_gst = product.price / (1 + gst_rate)
        gst_amount = product.price - price_before_gst
        item_total_before_gst = price_before_gst * quantity
        item_gst_total = gst_amount * quantity
        item_total_after_gst = product.price * quantity

        # Update order totals
        total_price_before_gst += item_total_before_gst
        total_gst += item_gst_total
        total_price_after_gst += item_total_after_gst
        total_quantity += quantity

        # Append each item's details to cart items
        cart_items.append({
            'id': product_id,
            'name': product.name,
            'image_url': product.image.url if product.image else "",
            'quantity': quantity,
            'price_before_gst': price_before_gst,
            'gst_amount': gst_amount,
            'price': product.price,
            'total': item_total_after_gst,
        })

    # Calculate subtotal
    subtotal = total_price_before_gst + total_gst

    # Render template with context data
    return render(request, 'order_detail.html', {
        'order': order,
        'cart_items': cart_items,
        'total_price_before_gst': total_price_before_gst,
        'total_gst': total_gst,
        'total_price_after_gst': total_price_after_gst,
        'total_quantity': total_quantity,
        'subtotal': subtotal,
        'search_query': search_query,
    })


@staff_member_required
def completed_orders_view(request):
    search_query = request.GET.get('search', '')
    completed_orders = Order.objects.filter(is_complete=True)

    if search_query:
        completed_orders = completed_orders.filter(
            Q(id__icontains=search_query) | Q(name__icontains=search_query)
        )

    return render(request, 'completed_orders.html', {
        'completed_orders': completed_orders,
        'search_query': search_query,
    })
