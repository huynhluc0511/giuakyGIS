from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ
    path('', views.home_view, name='home'),
    
    # Các đường dẫn món ăn
    path('do-uong/', views.do_uong_view, name='do_uong'),
    path('ga-chien/', views.ga_chien_view, name='ga_chien'),
    path('hamburger/', views.hamburger_view, name='hamburger'),
    path('khoai-tay/', views.khoai_tay_view, name='khoai_tay'),
    path('pizza/', views.pizza_view, name='pizza'),
    
    # Các đường dẫn chức năng
    path('gio-hang/', views.gio_hang_view, name='gio_hang'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('map/', views.map_view, name='map'),
    path('tinh-trang/', views.tinh_trang_view, name='tinh_trang'),
]