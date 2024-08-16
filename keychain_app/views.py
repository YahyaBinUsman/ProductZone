# views.py
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.conf import settings
from .models import Clothes, KeyChain, Wallet, Order
import logging
from django.urls import reverse

logger = logging.getLogger(__name__)
def home(request):
    featured_products = {
        'clothes': Clothes.objects.filter(is_featured=True),
        'keychains': KeyChain.objects.filter(is_featured=True),
        'wallets': Wallet.objects.filter(is_featured=True),
        'wrist_watches': WristWatch.objects.filter(is_featured=True),
        'hosiery': Hosiery.objects.filter(is_featured=True),
        'belts': Belt.objects.filter(is_featured=True),
    }
    return render(request, 'home.html', {'featured_products': featured_products})


def clothes(request):
    clothes_list = Clothes.objects.all()
    return render(request, 'clothes.html', {'clothes_list': clothes_list})

def keychains(request):
    keychains_list = KeyChain.objects.all()
    return render(request, 'keychains.html', {'keychains_list': keychains_list})

def wallets(request):
    wallets_list = Wallet.objects.all()
    return render(request, 'wallets.html', {'wallets_list': wallets_list})

def contact(request):
    return render(request, 'contact.html')

from django.shortcuts import redirect

def product_redirect(request, category, product_id):
    category_urls = {
        'clothes': 'clothes',
        'keychains': 'keychains',
        'wallets': 'wallets',
        'wrist_watches': 'wrist_watches',
        'hosiery': 'hosiery',
        'belts': 'belts',
    }
    
    if category not in category_urls:
        return redirect('home')  # Or a 404 page

    category_path = category_urls[category]
    return redirect(f'/{category}/?product_id={product_id}')


# views.py
from .models import KeyChain

def add_keychain_to_cart(request, keychain_id):
    if request.method == 'POST':
        quantity = int(request.POST.get(f'quantity_keychain_{keychain_id}', 1))
        
        try:
            keychain = KeyChain.objects.get(pk=keychain_id)
            if quantity > keychain.quantity:
                messages.error(request, "Quantity entered is greater than available stock.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            # Deduct the quantity from the original quantity
            keychain.quantity -= quantity
            keychain.save()

            # Add item to cart
            cart = request.session.get('cart', {})
            if str(keychain_id) in cart:
                cart[str(keychain_id)] += quantity
            else:
                cart[str(keychain_id)] = quantity
            request.session['cart'] = cart

            messages.success(request, f"{quantity} {keychain.name}(s) added to your cart.")

        except KeyChain.DoesNotExist:
            messages.error(request, "Keychain not found.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


# Add the following import statement
from .models import Wallet

# Add the following view function
def add_wallet_to_cart(request, wallet_id):
    if request.method == 'POST':
        quantity = int(request.POST.get(f'quantity_wallet_{wallet_id}', 1))
        
        try:
            wallet = Wallet.objects.get(pk=wallet_id)
            if quantity > wallet.quantity:
                messages.error(request, "Quantity entered is greater than available stock.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            # Deduct the quantity from the original quantity
            wallet.quantity -= quantity
            wallet.save()

            # Add item to cart
            cart = request.session.get('cart', {})
            if str(wallet_id) in cart:
                cart[str(wallet_id)] += quantity
            else:
                cart[str(wallet_id)] = quantity
            request.session['cart'] = cart

            messages.success(request, f"{quantity} {wallet.name}(s) added to your cart.")

        except Wallet.DoesNotExist:
            messages.error(request, "Wallet not found.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

from .models import Clothes, KeyChain, Wallet
from django.contrib import messages

from django.http import JsonResponse

from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib import messages
from .models import Clothes, KeyChain, Wallet, WristWatch, Hosiery, Belt

def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        try:
            # Check which model the product belongs to and retrieve accordingly
            if 'keychain' in request.POST:
                product = KeyChain.objects.get(pk=product_id)
            elif 'wallet' in request.POST:
                product = Wallet.objects.get(pk=product_id)
            elif 'wristwatch' in request.POST:
                product = WristWatch.objects.get(pk=product_id)
            elif 'hosiery' in request.POST:
                product = Hosiery.objects.get(pk=product_id)
            elif 'belt' in request.POST:
                product = Belt.objects.get(pk=product_id)
            else:
                product = Clothes.objects.get(pk=product_id)
            
            # Check quantity availability
            if quantity > product.quantity:
                messages.error(request, 'Quantity entered is greater than available stock.')
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            # Deduct the quantity from the original quantity
            product.quantity -= quantity
            product.save()

            # Add item to cart
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)] += quantity
            else:
                cart[str(product_id)] = quantity
            request.session['cart'] = cart

            # Construct the success message
            success_message = f"{quantity} {product.name}(s) added to your cart."
            messages.success(request, success_message)

            # Redirect to the previous page
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        except (KeyChain.DoesNotExist, Wallet.DoesNotExist, Clothes.DoesNotExist, WristWatch.DoesNotExist, Hosiery.DoesNotExist, Belt.DoesNotExist):
            messages.error(request, 'Product not found.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    messages.error(request, 'Invalid request method.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))
from .models import Clothes, KeyChain, Wallet, WristWatch, Hosiery, Belt
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price_before_gst = Decimal(0)
    total_gst = Decimal(0)
    total_price_after_gst = Decimal(0)
    total_quantity = 0

    for product_id, quantity in cart.items():
        try:
            product_id_numeric = int(product_id.split('_')[-1])
            product = Clothes.objects.get(pk=product_id_numeric)
        except (Clothes.DoesNotExist, ValueError):
            try:
                product_id_numeric = int(product_id.split('_')[-1])
                product = KeyChain.objects.get(pk=product_id_numeric)
            except (KeyChain.DoesNotExist, ValueError):
                try:
                    product_id_numeric = int(product_id.split('_')[-1])
                    product = Wallet.objects.get(pk=product_id_numeric)
                except (Wallet.DoesNotExist, ValueError):
                    try:
                        product_id_numeric = int(product_id.split('_')[-1])
                        product = WristWatch.objects.get(pk=product_id_numeric)
                    except (WristWatch.DoesNotExist, ValueError):
                        try:
                            product_id_numeric = int(product_id.split('_')[-1])
                            product = Hosiery.objects.get(pk=product_id_numeric)
                        except (Hosiery.DoesNotExist, ValueError):
                            try:
                                product_id_numeric = int(product_id.split('_')[-1])
                                product = Belt.objects.get(pk=product_id_numeric)
                            except (Belt.DoesNotExist, ValueError):
                                continue

        gst_rate = Decimal(settings.GST_RATE)
        price_before_gst = product.price * (Decimal(1) - gst_rate)
        gst_amount = product.price - price_before_gst
        total_price_before_gst += price_before_gst
        total_gst += gst_amount
        total_price_after_gst += product.price * Decimal(quantity)
        total_quantity += quantity

        cart_items.append({
            'id': product_id,
            'name': f"{product.name} ({quantity})",
            'price_before_gst': str(price_before_gst),
            'gst_amount': str(gst_amount),
            'price': str(product.price),
            'quantity': quantity,
            'total': str(product.price * Decimal(quantity)),  # Calculate total for the current item
        })

    subtotal = total_price_before_gst + total_gst  # Calculate subtotal

    request.session['total_price'] = str(subtotal)
    request.session['cart_items'] = cart_items

    return render(request, 'view_cart.html', {
        'cart_items': cart_items,
        'total_price_before_gst': total_price_before_gst,
        'total_gst': total_gst,
        'total_price_after_gst': total_price_after_gst,
        'total_quantity': total_quantity,
        'subtotal': subtotal,
    })

def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        try:
            # Check which model the product belongs to and retrieve accordingly
            if Clothes.objects.filter(pk=product_id).exists():
                product = Clothes.objects.get(pk=product_id)
            elif Wallet.objects.filter(pk=product_id).exists():
                product = Wallet.objects.get(pk=product_id)
            elif KeyChain.objects.filter(pk=product_id).exists():
                product = KeyChain.objects.get(pk=product_id)
            elif WristWatch.objects.filter(pk=product_id).exists():
                product = WristWatch.objects.get(pk=product_id)
            elif Hosiery.objects.filter(pk=product_id).exists():
                product = Hosiery.objects.get(pk=product_id)
            elif Belt.objects.filter(pk=product_id).exists():
                product = Belt.objects.get(pk=product_id)
            else:
                raise ValueError("Product not found.")

            # Check if the product is in the cart
            cart = request.session.get('cart', {})
            if product_id in cart:
                # Ensure the quantity to be removed doesn't exceed the quantity in the cart
                cart_quantity = cart[product_id]
                if cart_quantity > 0:
                    # Add the deducted quantity back to the product stock
                    product.quantity += 1
                    product.save()

                    # Update the quantity in the cart
                    cart[product_id] -= 1
                    if cart[product_id] <= 0:
                        del cart[product_id]

                    # Save the updated cart in the session
                    request.session['cart'] = cart
                    messages.success(request, "Product quantity reduced in your cart.")
                else:
                    raise ValueError("There are no more units of this product in your cart.")
            else:
                messages.error(request, "Product is not in your cart.")

        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, "An error occurred while processing the request.")

    return redirect('view_cart')

def checkout(request):
    cart_items = request.session.get('cart_items', [])
    total_price = request.session.get('total_price', Decimal(0))

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction
from django.conf import settings

def process_order(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')  # Get the customer's email
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        country = 'Pakistan'  # Set country to Pakistan
        payment = 'Cash on Delivery'  # Set payment to Cash on Delivery
        total_price_after_gst = Decimal(request.POST.get('total_price', 0))
        cart_items = request.session.get('cart_items', [])
        products_data = [(item['id'], item['quantity']) for item in cart_items]

        # Calculate total_price_after_gst
        total_price_after_gst = Decimal(0)
        for item in cart_items:
            total_price_after_gst += Decimal(item['total'])

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
                    total_price_after_gst=total_price_after_gst  # Save total_price_after_gst
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
                for product_id, quantity in products_data:
                    try:
                        if 'clothes' in product_id:  # Check if the product is from the clothes page
                            product = Clothes.objects.select_for_update().get(pk=product_id.split('_')[-1])
                        elif 'keychain' in product_id:
                            product = KeyChain.objects.select_for_update().get(pk=product_id.split('_')[-1])
                        elif 'wallet' in product_id:
                            product = Wallet.objects.select_for_update().get(pk=product_id.split('_')[-1])
                        elif 'wristwatch' in product_id:
                            product = WristWatch.objects.select_for_update().get(pk=product_id.split('_')[-1])
                        elif 'hosiery' in product_id:
                            product = Hosiery.objects.select_for_update().get(pk=product_id.split('_')[-1])
                        elif 'belt' in product_id:
                            product = Belt.objects.select_for_update().get(pk=product_id.split('_')[-1])
                        else:
                            continue  # Skip if the product type is unknown
                        
                        # Ensure that the quantity to be deducted does not exceed the quantity in the cart
                        cart_quantity = min(quantity, product.quantity)
                        # Deduct the cart quantity from the product stock
                        product.quantity -= cart_quantity
                        product.save()
                    except (KeyChain.DoesNotExist, Wallet.DoesNotExist, Clothes.DoesNotExist,
                            WristWatch.DoesNotExist, Hosiery.DoesNotExist, Belt.DoesNotExist):
                        # Log error or handle as needed
                        pass

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
                    f"Ordered Products:\n"
                )
                for product in products:
                    message_owner += f"- {product}\n"
                
                message_owner += f"\nTotal Price: ${total_price_after_gst}"

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
                    f"Ordered Products:\n"
                )
                for product in products:
                    message_customer += f"- {product}\n"

                message_customer += f"\nTotal Price: ${total_price_after_gst}\n\n"
                message_customer += "Your order will be delivered soon. Thank you for shopping with us!\n\n"
                message_customer += "Best regards,\nYour Company Name"

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

    
def error_page(request):
    return render(request,'error.html')

def order_success(request):
    return render(request, 'order_success.html')

from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render, get_object_or_404, redirect
from .models import Clothes, KeyChain, Wallet
from django.contrib import messages

@staff_member_required
def products_view(request):
    products = (
        list(Clothes.objects.all()) +
        list(KeyChain.objects.all()) +
        list(Wallet.objects.all()) +
        list(WristWatch.objects.all()) +
        list(Hosiery.objects.all()) +
        list(Belt.objects.all())
    )
    return render(request, 'products.html', {'products': products})
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Max
from .models import Clothes, KeyChain, Wallet, WristWatch, Hosiery, Belt

def generate_unique_id():
    max_id = 0

    # Get the maximum ID from each table and keep track of the highest one
    max_id = max(max_id, Clothes.objects.aggregate(Max('id'))['id__max'] or 0)
    max_id = max(max_id, KeyChain.objects.aggregate(Max('id'))['id__max'] or 0)
    max_id = max(max_id, Wallet.objects.aggregate(Max('id'))['id__max'] or 0)
    max_id = max(max_id, WristWatch.objects.aggregate(Max('id'))['id__max'] or 0)
    max_id = max(max_id, Hosiery.objects.aggregate(Max('id'))['id__max'] or 0)
    max_id = max(max_id, Belt.objects.aggregate(Max('id'))['id__max'] or 0)

    return max_id + 1

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        category = request.POST['category']
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        quantity = request.POST['quantity']
        image = request.FILES.get('image')
        
        unique_id = generate_unique_id()

        product_data = {
            'id': unique_id,
            'name': name,
            'description': description,
            'price': price,
            'quantity': quantity,
            'image': image,
        }

        if category == 'Clothes':
            Clothes.objects.create(**product_data)
        elif category == 'KeyChain':
            KeyChain.objects.create(**product_data)
        elif category == 'Wallet':
            Wallet.objects.create(**product_data)
        elif category == 'WristWatches':
            WristWatch.objects.create(**product_data)
        elif category == 'Hosiery':
            Hosiery.objects.create(**product_data)
        elif category == 'Belts':
            Belt.objects.create(**product_data)
        
        messages.success(request, 'Product added successfully.')
        return redirect('products_view')

    return render(request, 'product_form.html')

from django.http import Http404

@staff_member_required
def edit_product(request, product_id):
    # Try to find the product in each model
    try:
        product = Clothes.objects.get(pk=product_id)
    except Clothes.DoesNotExist:
        try:
            product = KeyChain.objects.get(pk=product_id)
        except KeyChain.DoesNotExist:
            try:
                product = Hosiery.objects.get(pk=product_id)
            except Hosiery.DoesNotExist:
                try:
                    product = Belt.objects.get(pk=product_id)
                except Belt.DoesNotExist:
                    try:
                        product = WristWatch.objects.get(pk=product_id)
                    except WristWatch.DoesNotExist:
                        try:
                            product = Wallet.objects.get(pk=product_id)
                        except Wallet.DoesNotExist:
                            # If none of the models contain the product, raise a 404 error
                            raise Http404("Product not found")

    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.quantity = request.POST['quantity']
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('products_view')

    return render(request, 'product_form.html', {'product': product})
from django.http import Http404

@staff_member_required
def delete_product(request, product_id):
    # Try to find the product in each model
    try:
        product = Clothes.objects.get(pk=product_id)
    except Clothes.DoesNotExist:
        try:
            product = KeyChain.objects.get(pk=product_id)
        except KeyChain.DoesNotExist:
            try:
                product = Hosiery.objects.get(pk=product_id)
            except Hosiery.DoesNotExist:
                try:
                    product = Belt.objects.get(pk=product_id)
                except Belt.DoesNotExist:
                    try:
                        product = WristWatch.objects.get(pk=product_id)
                    except WristWatch.DoesNotExist:
                        try:
                            product = Wallet.objects.get(pk=product_id)
                        except Wallet.DoesNotExist:
                            # If none of the models contain the product, raise a 404 error
                            raise Http404("Product not found")

    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('products_view')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, Clothes, KeyChain, Wallet
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q
@staff_member_required
def order_details(request):
    search_query = request.GET.get('search', '')
    
    # Fetch all orders
    all_orders = Order.objects.all()
    
    # Apply search filter if a search query is provided
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
    total_pending_orders = pending_orders.count()

    completed_orders = all_orders.filter(is_complete=True)
    total_sales = sum(order.total_price_after_gst for order in completed_orders)
    potential_sales = sum(order.total_price_after_gst for order in pending_orders)

    return render(request, 'order_details.html', {
        'pending_orders': pending_orders,
        'total_orders': total_orders,
        'total_pending_orders': total_pending_orders,
        'total_sales': total_sales,
        'potential_sales': potential_sales,
        'search_query': search_query,
    })

@staff_member_required
def mark_order_complete(request, order_id):
    # Fetch the order using order_id
    order = get_object_or_404(Order, id=order_id)
    
    # Mark the order as complete
    order.is_complete = True
    order.save()
    
    # Display a success message
    messages.success(request, f"Order #{order.id} marked as complete.")
    
    return redirect('order_details')

@staff_member_required
def products_overview(request):
    search_query = request.GET.get('search', '')

    clothes = Clothes.objects.all()
    keychains = KeyChain.objects.all()
    wallets = Wallet.objects.all()
    wrist_watches = WristWatch.objects.all()
    hosiery = Hosiery.objects.all()
    belts = Belt.objects.all()

    # Apply search filter if a search query is provided
    if search_query:
        clothes = clothes.filter(name__icontains=search_query)
        keychains = keychains.filter(name__icontains=search_query)
        wallets = wallets.filter(name__icontains=search_query)
        wrist_watches = wrist_watches.filter(name__icontains=search_query)
        hosiery = hosiery.filter(name__icontains=search_query)
        belts = belts.filter(name__icontains=search_query)

    # Handle feature toggle
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_type = request.POST.get('product_type')
        action = request.POST.get('action')

        if product_type == 'clothes':
            product = Clothes.objects.get(id=product_id)
        elif product_type == 'keychains':
            product = KeyChain.objects.get(id=product_id)
        elif product_type == 'wallets':
            product = Wallet.objects.get(id=product_id)
        elif product_type == 'wrist_watches':
            product = WristWatch.objects.get(id=product_id)
        elif product_type == 'hosiery':
            product = Hosiery.objects.get(id=product_id)
        elif product_type == 'belts':
            product = Belt.objects.get(id=product_id)

        if action == 'feature':
            if Clothes.objects.filter(is_featured=True).count() + KeyChain.objects.filter(is_featured=True).count() + Wallet.objects.filter(is_featured=True).count() + WristWatch.objects.filter(is_featured=True).count() + Hosiery.objects.filter(is_featured=True).count() + Belt.objects.filter(is_featured=True).count() < 12:
                product.is_featured = True
                product.save()
        elif action == 'remove':
            product.is_featured = False
            product.save()

    # Calculate total items, quantities, and price sum for each category
    clothes_count = clothes.count()
    keychains_count = keychains.count()
    wallets_count = wallets.count()
    wrist_watches_count = wrist_watches.count()
    hosiery_count = hosiery.count()
    belts_count = belts.count()

    clothes_quantity = sum(item.quantity for item in clothes)
    keychains_quantity = sum(item.quantity for item in keychains)
    wallets_quantity = sum(item.quantity for item in wallets)
    wrist_watches_quantity = sum(item.quantity for item in wrist_watches)
    hosiery_quantity = sum(item.quantity for item in hosiery)
    belts_quantity = sum(item.quantity for item in belts)

    clothes_total_price = sum(item.price * item.quantity for item in clothes)
    keychains_total_price = sum(item.price * item.quantity for item in keychains)
    wallets_total_price = sum(item.price * item.quantity for item in wallets)
    wrist_watches_total_price = sum(item.price * item.quantity for item in wrist_watches)
    hosiery_total_price = sum(item.price * item.quantity for item in hosiery)
    belts_total_price = sum(item.price * item.quantity for item in belts)

    # Overall total for all categories combined
    total_items = (
        clothes_count + keychains_count + wallets_count +
        wrist_watches_count + hosiery_count + belts_count
    )
    total_quantity = (
        clothes_quantity + keychains_quantity + wallets_quantity +
        wrist_watches_quantity + hosiery_quantity + belts_quantity
    )
    total_price_sum = (
        clothes_total_price + keychains_total_price + wallets_total_price +
        wrist_watches_total_price + hosiery_total_price + belts_total_price
    )

    return render(request, 'products_overview.html', {
        'clothes': clothes,
        'keychains': keychains,
        'wallets': wallets,
        'wrist_watches': wrist_watches,
        'hosiery': hosiery,
        'belts': belts,
        'clothes_count': clothes_count,
        'keychains_count': keychains_count,
        'wallets_count': wallets_count,
        'wrist_watches_count': wrist_watches_count,
        'hosiery_count': hosiery_count,
        'belts_count': belts_count,
        'clothes_quantity': clothes_quantity,
        'keychains_quantity': keychains_quantity,
        'wallets_quantity': wallets_quantity,
        'wrist_watches_quantity': wrist_watches_quantity,
        'hosiery_quantity': hosiery_quantity,
        'belts_quantity': belts_quantity,
        'clothes_total_price': clothes_total_price,
        'keychains_total_price': keychains_total_price,
        'wallets_total_price': wallets_total_price,
        'wrist_watches_total_price': wrist_watches_total_price,
        'hosiery_total_price': hosiery_total_price,
        'belts_total_price': belts_total_price,
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_price_sum': total_price_sum,
        'search_query': search_query,
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import WristWatch, Hosiery, Belt

# Display Views
def wrist_watches(request):
    wrist_watches_list = WristWatch.objects.all()
    return render(request, 'wrist_watches.html', {'wrist_watches_list': wrist_watches_list})

def hosiery(request):
    hosiery_list = Hosiery.objects.all()
    return render(request, 'hosiery.html', {'hosiery_list': hosiery_list})

def belts(request):
    belts_list = Belt.objects.all()
    return render(request, 'belts.html', {'belts_list': belts_list})

# Add to Cart Views
def add_wrist_watch_to_cart(request, wrist_watch_id):
    if request.method == 'POST':
        quantity = int(request.POST.get(f'quantity_wrist_watch_{wrist_watch_id}', 1))
        
        try:
            wrist_watch = WristWatch.objects.get(pk=wrist_watch_id)
            if quantity > wrist_watch.quantity:
                messages.error(request, "Quantity entered is greater than available stock.")
                return redirect(request.META.get('HTTP_REFERER', 'wrist_watches'))

            # Deduct the quantity from the original quantity
            wrist_watch.quantity -= quantity
            wrist_watch.save()

            # Add item to cart
            cart = request.session.get('cart', {})
            if str(wrist_watch_id) in cart:
                cart[str(wrist_watch_id)] += quantity
            else:
                cart[str(wrist_watch_id)] = quantity
            request.session['cart'] = cart

            messages.success(request, f"{quantity} {wrist_watch.name}(s) added to your cart.")

        except WristWatch.DoesNotExist:
            messages.error(request, "Wrist watch not found.")

    return redirect(request.META.get('HTTP_REFERER', 'wrist_watches'))

def add_hosiery_to_cart(request, hosiery_id):
    if request.method == 'POST':
        quantity = int(request.POST.get(f'quantity_hosiery_{hosiery_id}', 1))
        
        try:
            hosiery_item = Hosiery.objects.get(pk=hosiery_id)
            if quantity > hosiery_item.quantity:
                messages.error(request, "Quantity entered is greater than available stock.")
                return redirect(request.META.get('HTTP_REFERER', 'hosiery'))

            # Deduct the quantity from the original quantity
            hosiery_item.quantity -= quantity
            hosiery_item.save()

            # Add item to cart
            cart = request.session.get('cart', {})
            if str(hosiery_id) in cart:
                cart[str(hosiery_id)] += quantity
            else:
                cart[str(hosiery_id)] = quantity
            request.session['cart'] = cart

            messages.success(request, f"{quantity} {hosiery_item.name}(s) added to your cart.")

        except Hosiery.DoesNotExist:
            messages.error(request, "Hosiery item not found.")

    return redirect(request.META.get('HTTP_REFERER', 'hosiery'))

def add_belt_to_cart(request, belt_id):
    if request.method == 'POST':
        quantity = int(request.POST.get(f'quantity_belt_{belt_id}', 1))
        
        try:
            belt = Belt.objects.get(pk=belt_id)
            if quantity > belt.quantity:
                messages.error(request, "Quantity entered is greater than available stock.")
                return redirect(request.META.get('HTTP_REFERER', 'belts'))

            # Deduct the quantity from the original quantity
            belt.quantity -= quantity
            belt.save()

            # Add item to cart
            cart = request.session.get('cart', {})
            if str(belt_id) in cart:
                cart[str(belt_id)] += quantity
            else:
                cart[str(belt_id)] = quantity
            request.session['cart'] = cart

            messages.success(request, f"{quantity} {belt.name}(s) added to your cart.")

        except Belt.DoesNotExist:
            messages.error(request, "Belt not found.")

    return redirect(request.META.get('HTTP_REFERER', 'belts'))

# views.py

from django.http import JsonResponse
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import Q

def search(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        # Search across all product types with quantity greater than 1
        clothes = Clothes.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)) & Q(quantity__gt=1)
        )
        keychains = KeyChain.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)) & Q(quantity__gt=1)
        )
        wallets = Wallet.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)) & Q(quantity__gt=1)
        )
        wrist_watches = WristWatch.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)) & Q(quantity__gt=1)
        )
        hosiery = Hosiery.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)) & Q(quantity__gt=1)
        )
        belts = Belt.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)) & Q(quantity__gt=1)
        )

        # Combine all the results with their respective categories
        all_products = [
            {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': 'clothes'} for p in clothes
        ] + [
            {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': 'keychains'} for p in keychains
        ] + [
            {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': 'wallets'} for p in wallets
        ] + [
            {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': 'wrist_watches'} for p in wrist_watches
        ] + [
            {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': 'hosiery'} for p in hosiery
        ] + [
            {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': 'belts'} for p in belts
        ]

        results = all_products

    return JsonResponse({'results': results})

