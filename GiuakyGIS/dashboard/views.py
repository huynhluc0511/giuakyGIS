

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
# Xóa dòng 'from requests import request' vì nó gây xung đột với tham số request của Django

# Model
from dashboard.models import Product, Store


# DRF
from rest_framework import viewsets, permissions
from .serializers import ProductSerializer

import requests 

# ================== WEB VIEW (HTML) ==================

# Hàm kiểm tra admin (Thêm kiểm tra is_authenticated để tránh lỗi khi chưa log in)
def admin_check(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(admin_check)
def dashboard_index(request):
    product_count = Product.objects.count()
    return render(request, 'dashboard/index.html', {
        'product_count': product_count
    })


@user_passes_test(admin_check)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'dashboard/product_list.html', {
        'products': products
    })

# ĐƯA HÀM NÀY RA NGOÀI CLASS VÀ THÊM DECORATOR KIỂM TRA QUYỀN
@user_passes_test(admin_check)
def manage_stores_view(request):
    # Logic để quản lý cửa hàng (hiển thị danh sách, v.v.)
    return render(request, 'dashboard/manage_stores.html')


# ================== API (DRF) ==================

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # GET → user login là xem được
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # POST, PUT, DELETE → chỉ admin
        return request.user and request.user.is_staff


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    # ĐÃ XÓA manage_stores_view KHỎI ĐÂY
    from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt # Tạm thời dùng để test nếu chưa xử lý được CSRF token ở frontend
def store_list_create(request):
    if request.method == 'POST':
        # Logic lưu cửa hàng ở đây
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Store
from .serializers import ProductSerializer

@api_view(['GET', 'POST']) # <--- Phải có 'POST' ở đây
def store_list_create(request):
    if request.method == 'GET':
        stores = Store.objects.all()
        serializer = ProductSerializer(stores, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

import requests 

def get_coords(address):
    # Dùng Nominatim (miễn phí, không cần key) để test cho nhanh
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
    headers = {'User-Agent': 'GisApp/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data:
            return {
                'lat': float(data[0]['lat']),
                'lng': float(data[0]['lon'])
            }
    except Exception as e:
        print(f"Lỗi Geocoding: {e}")
    return None
        


