from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'products',   views.ProductViewSet,  basename='product')
router.register(r'stores',     views.StoreViewSet,    basename='store')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'orders',     views.OrderViewSet,    basename='order_api')

app_name = 'dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_index, name='index'),

    # Stores
    path('stores/',                views.stores_list,   name='stores_list'),
    path('stores/create/',         views.stores_create, name='stores_create'),
    path('stores/<int:pk>/',       views.stores_detail, name='stores_detail'),
    path('stores/<int:pk>/edit/',  views.stores_edit,   name='stores_edit'),
    path('stores/<int:pk>/delete/',views.stores_delete, name='stores_delete'),

    # Categories
    path('categories/',                views.categories_list,   name='categories_list'),
    path('categories/create/',         views.categories_create, name='categories_create'),
    path('categories/<int:pk>/edit/',  views.categories_edit,   name='categories_edit'),
    path('categories/<int:pk>/delete/',views.categories_delete, name='categories_delete'),

    # Products
    path('products/',                views.products_list,   name='products_list'),
    path('products/create/',         views.products_create, name='products_create'),
    path('products/<int:pk>/',       views.products_detail, name='products_detail'),
    path('products/<int:pk>/edit/',  views.products_edit,   name='products_edit'),
    path('products/<int:pk>/delete/',views.products_delete, name='products_delete'),

    # Orders
    path('orders/',                views.orders_list,   name='orders_list'),
    path('orders/create/',         views.orders_create, name='orders_create'),
    path('orders/<int:pk>/',       views.orders_detail, name='orders_detail'),
    path('orders/<int:pk>/edit/',  views.orders_edit,   name='orders_edit'),
    path('orders/<int:pk>/delete/',views.orders_delete, name='orders_delete'),

    # Users
    path('users/',                views.users_list,   name='users_list'),
    path('users/create/',         views.users_create, name='users_create'),
    path('users/<int:pk>/',       views.users_detail, name='users_detail'),
    path('users/<int:pk>/edit/',  views.users_edit,   name='users_edit'),
    path('users/<int:pk>/delete/',views.users_delete, name='users_delete'),

    # Warehouse
    path('warehouse/',                     views.warehouse_list,            name='warehouse_list'),
    path('warehouse/<int:pk>/',            views.warehouse_detail,          name='warehouse_detail'),
    path('warehouse/create/',              views.warehouse_create,          name='warehouse_create'),
    path('warehouse/<int:pk>/edit/',       views.warehouse_edit,            name='warehouse_edit'),
    path('warehouse/<int:pk>/delete/',     views.warehouse_delete,          name='warehouse_delete'),

    # Warehouse Item
    path('warehouse-item/create/',         views.warehouse_item_create,     name='warehouse_item_create'),
    path('warehouse-item/<int:pk>/edit/',  views.warehouse_item_edit,       name='warehouse_item_edit'),
    path('warehouse-item/<int:pk>/delete/',views.warehouse_item_delete,     name='warehouse_item_delete'),

    # Warehouse Transaction
    path('warehouse-transaction/create/',      views.warehouse_transaction_create,  name='warehouse_transaction_create'),
    path('warehouse-transaction/<int:pk>/delete/', views.warehouse_transaction_delete, name='warehouse_transaction_delete'),

    # Warehouse Batch (NEW)
    path('warehouse-batch/',                           views.warehouse_batch_list,        name='warehouse_batch_list'),
    path('warehouse-batch/create/',                    views.warehouse_batch_create,      name='warehouse_batch_create'),
    path('warehouse-batch/template-excel/<int:warehouse_id>/', views.warehouse_batch_template_excel, name='warehouse_batch_template_excel'),
    path('warehouse-batch/<int:pk>/add-items/',        views.warehouse_batch_add_items,   name='warehouse_batch_add_items'),
    path('warehouse-batch/<int:pk>/',                  views.warehouse_batch_detail,      name='warehouse_batch_detail'),
    path('warehouse-batch/<int:pk>/print/',            views.warehouse_batch_print,       name='warehouse_batch_print'),
    path('warehouse-batch/<int:pk>/export-excel/',     views.warehouse_batch_export_excel, name='warehouse_batch_export_excel'),
    path('warehouse-batch/<int:pk>/delete/',           views.warehouse_batch_delete,      name='warehouse_batch_delete'),
    path('warehouse-batch-item/<int:pk>/delete/',      views.warehouse_batch_item_delete, name='warehouse_batch_item_delete'),
    path('warehouse/import-excel/',                    views.warehouse_import_excel,      name='warehouse_import_excel'),

    # Search & API
    path('api/search/stores/',            views.api_search_stores,       name='api_search_stores'),
    path('api/search/alley/',             views.api_search_by_alley,     name='api_search_alley'),
    path('api/warehouse/low-stock/',      views.api_warehouse_low_stock, name='api_low_stock'),

    # REST Framework
    path('api/', include(router.urls)),
    path('api/stores-create/', views.store_list_create, name='store_api'),
    
    # Manage stores (full-featured page)
    path('manage/', views.manage_stores_view, name='manage_stores'),
    
    # About/Introduction Management
    path('about/', views.about_list, name='about_list'),
    path('about/create/', views.about_create, name='about_create'),
    path('about/<int:pk>/', views.about_detail, name='about_detail'),
    path('about/<int:pk>/edit/', views.about_edit, name='about_edit'),
    path('about/<int:pk>/delete/', views.about_delete, name='about_delete'),
    path('about/import/', views.about_import, name='about_import'),
    
    # News Management
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),
    path('news/<int:pk>/toggle-status/', views.news_toggle_status, name='news_toggle_status'),
    path('news/<int:pk>/toggle-featured/', views.news_toggle_featured, name='news_toggle_featured'),
    
    # Review Management
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:pk>/', views.review_detail, name='review_detail'),
    path('reviews/<int:pk>/approve/', views.review_approve, name='review_approve'),
    path('reviews/<int:pk>/reject/', views.review_reject, name='review_reject'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    
    # Order Review Management
    path('order-reviews/', views.order_review_list, name='order_review_list'),
    path('order-reviews/<int:pk>/', views.order_review_detail, name='order_review_detail'),
    path('order-reviews/<int:pk>/approve/', views.order_review_approve, name='order_review_approve'),
    path('order-reviews/<int:pk>/reject/', views.order_review_reject, name='order_review_reject'),
    path('order-reviews/<int:pk>/delete/', views.order_review_delete, name='order_review_delete'),
    
    # Shipper Management
    path('shippers/', views.shippers_list, name='shippers_list'),
    path('shippers/create/', views.shipper_create, name='shipper_create'),
    path('shippers/<int:pk>/', views.shipper_detail, name='shipper_detail'),
    path('shippers/<int:pk>/edit/', views.shipper_edit, name='shipper_edit'),
    path('shippers/<int:pk>/delete/', views.shipper_delete, name='shipper_delete'),
    path('shippers/<int:pk>/toggle-status/', views.shipper_toggle_status, name='shipper_toggle_status'),
    
    # Delivery Status Management
    path('delivery-status/', views.delivery_status_list, name='delivery_status_list'),
    path('delivery-status/<int:pk>/', views.delivery_status_detail, name='delivery_status_detail'),
    path('delivery-status/<int:pk>/assign/', views.delivery_status_assign, name='delivery_status_assign'),
    
    # Order Shipper Assignment
    path('orders/<int:pk>/assign-shipper/', views.orders_assign_shipper, name='orders_assign_shipper'),
    path('orders/<int:pk>/notify-shippers/', views.orders_notify_shippers, name='orders_notify_shippers'),
]
