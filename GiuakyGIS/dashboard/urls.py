from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 1. Khai báo Router cho API (Sử dụng ProductViewSet)
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

app_name = 'dashboard' # Giúp dùng {% url 'dashboard:manage_stores' %} trong HTML

urlpatterns = [
    # ================== CÁC TRANG GIAO DIỆN (HTML) ==================
    # Các trang này gọi trực tiếp từ hàm trong views.py (Function-based views)
    path('', views.dashboard_index, name='index'),
    path('products/', views.product_list, name='product_list'),
    
    # ĐÂY LÀ DÒNG BẠN CẦN SỬA: Gọi trực tiếp hàm manage_stores_view
    path('manage_stores/', views.manage_stores_view, name='manage_stores'),

    # ================== CÁC ĐƯỜNG DẪN API (JSON) ===================
    # API sẽ nằm ở đường dẫn: /dashboard/api/products/
    path('api/', include(router.urls)),
    path('api/stores/', views.store_list_create, name='store_api'),
]


