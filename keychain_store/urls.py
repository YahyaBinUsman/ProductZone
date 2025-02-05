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
    path('search/', views.search, name='search'),
    path('edit-category/<int:pk>/', views.edit_category, name='edit_category'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('completed_orders/', views.completed_orders_view, name='completed_orders'),
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('send-newsletter/', views.send_newsletter, name='send_newsletter'),
    path('all/', views.all_categories_products, name='all_categories_products'),
    path('all-products/', views.all_products_view, name='all_products'),
    path('billing/', views.billing_page, name='billing_page'),  # Billing page for generating bills
    path('receipt/<int:receipt_id>/', views.generate_receipt, name='generate_receipt'),  # Receipt view
    path('get-product-by-barcode/<str:barcode>/', views.get_product_by_barcode, name='get_product_by_barcode'),
    path('billing-page/', views.billing_page, name='billing_page'),
    path('billing-history/', views.billing_history, name='billing_history'),
    path('deduct-stock/<str:barcode>/', views.deduct_stock, name='deduct_stock'),
    path('barcode/generate/', views.barcode_generation_page, name='barcode_generation'),
    path('restore-stock/<str:barcode>/', views.restore_stock, name='restore_stock'),
    path("sales-overview/", views.sales_overview, name="sales_overview"),
    path('generate_sales_pdf/', views.generate_sales_report, name='generate_sales_pdf'),
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
