from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn trang chủ (hiển thị file home.html)
    path('', views.index, name='trang_chu'),
    
    # Đường dẫn trang bản đồ (hiển thị file map.html)
    path('ban-do/', views.view_ban_do, name='ban_do'),
]