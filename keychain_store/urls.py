# keychain_store/urls.py
from django.contrib import admin
from django.urls import path
from keychain_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('view-cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_product_to_cart, name='add_product_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-order/', views.process_order, name='process_order'),
    path('error/', views.error_page, name='error_page'),
    path('success/', views.order_success, name='order_success'),
    path('products/', views.products_view, name='products_view'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('products/overview/', views.products_overview, name='products_overview'),
    path('order-details/', views.order_details, name='order_details'),
    path('mark-order-complete/<int:order_id>/', views.mark_order_complete, name='mark_order_complete'),
    path('categories/', views.category_list, name='category_list'),
    path('add-category/', views.add_category, name='add_category'),
    path('faqs/', views.faqs, name='faqs'),
    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),
path('category/<str:category>/product/<int:product_id>/', views.product_redirect, name='product_redirect'),
    path('category/<str:url_name>/', views.category_detail, name='category_detail'),
 path('search/', views.search, name='search')

]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
