from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn cho trang chủ (để trống chuỗi đầu tiên đại diện cho trang gốc)
    path('', views.home_view, name='home'),
]
