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
    path('warehouse/',                views.warehouse_list,   name='warehouse_list'),
    path('warehouse/create/',         views.warehouse_create, name='warehouse_create'),
    path('warehouse/<int:pk>/',       views.warehouse_detail, name='warehouse_detail'),
    path('warehouse/<int:pk>/edit/',  views.warehouse_edit,   name='warehouse_edit'),
    path('warehouse/<int:pk>/delete/',views.warehouse_delete, name='warehouse_delete'),
    
    # Warehouse Item
    path('warehouse/item/create/',        views.warehouse_item_create, name='warehouse_item_create'),
    path('warehouse/item/<int:pk>/edit/', views.warehouse_item_edit,   name='warehouse_item_edit'),
    path('warehouse/item/<int:pk>/delete/',views.warehouse_item_delete, name='warehouse_item_delete'),
    
    # Warehouse Transaction
    path('warehouse/transaction/create/',         views.warehouse_transaction_create, name='warehouse_transaction_create'),
    path('warehouse/transaction/<int:pk>/delete/',views.warehouse_transaction_delete, name='warehouse_transaction_delete'),

    # Manage stores (full-featured page)
    path('manage/', views.manage_stores_view, name='manage_stores'),

    # API (DRF)
    path('api/', include(router.urls)),
    path('api/stores-create/', views.store_list_create, name='store_api'),
]
