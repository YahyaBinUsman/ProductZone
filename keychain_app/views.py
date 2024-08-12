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
    return render(request, 'home.html')

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

def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        try:
            # Check which model the product belongs to and retrieve accordingly
            if 'keychain' in request.POST:
                product = KeyChain.objects.get(pk=product_id)
            elif 'wallet' in request.POST:
                product = Wallet.objects.get(pk=product_id)
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
        
        except (KeyChain.DoesNotExist, Wallet.DoesNotExist, Clothes.DoesNotExist):
            messages.error(request, 'Product not found.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    messages.error(request, 'Invalid request method.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

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
from .models import Clothes, KeyChain, Wallet

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
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.db import transaction
from .models import Order, Clothes, KeyChain, Wallet
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
                        else:
                            continue  # Skip if the product type is unknown
                        
                        # Ensure that the quantity to be deducted does not exceed the quantity in the cart
                        cart_quantity = min(quantity, product.quantity)
                        # Deduct the cart quantity from the product stock
                        product.quantity -= cart_quantity
                        product.save()
                    except (KeyChain.DoesNotExist, Wallet.DoesNotExist, Clothes.DoesNotExist):
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