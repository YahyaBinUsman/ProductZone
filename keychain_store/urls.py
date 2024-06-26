# keychain_store/urls.py
from django.contrib import admin
from django.urls import path
from keychain_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('clothes/', views.clothes, name='clothes'),
    path('keychains/', views.keychains, name='keychains'),
    path('wallets/', views.wallets, name='wallets'),
    path('contact/', views.contact, name='contact'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart_with_id'),
    path('view-cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-order/', views.process_order, name='process_order'),
    path('error/', views.error_page, name='error_page'),
    path('success/', views.order_success, name='order_success'),
    path('add_keychain_to_cart/<int:keychain_id>/', views.add_keychain_to_cart, name='add_keychain_to_cart'),
    path('add_wallet_to_cart/<int:wallet_id>/', views.add_wallet_to_cart, name='add_wallet_to_cart'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
