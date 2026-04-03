from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('do-uong/', views.do_uong_view, name='do_uong'),
    path('ga-chien/', views.ga_chien_view, name='ga_chien'),
    path('hamburger/', views.hamburger_view, name='hamburger'),
    path('khoai-tay/', views.khoai_tay_view, name='khoai_tay'),
    path('pizza/', views.pizza_view, name='pizza'),
    path('gio-hang/', views.gio_hang_view, name='gio_hang'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('lien-he/', views.lien_he_view, name='lien_he'),
    path('tinh-trang/', views.tinh_trang_view, name='tinh_trang'),
    path('tim-duong/', views.tim_duong_view, name='tim_duong'),
]
