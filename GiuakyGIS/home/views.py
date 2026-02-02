from django.shortcuts import render
from django.core.serializers import serialize
from .models import SanPham, CuaHang

# Logic cho trang chủ (Menu món ăn)
def index(request):
    danh_sach_mon = SanPham.objects.all() # Lấy tất cả món ăn (ORM)
    return render(request, 'home/index.html', {'mon_an': danh_sach_mon})

# Logic cho trang bản đồ (GIS)
def view_ban_do(request):
    # Lấy dữ liệu cửa hàng, chuyển thành GeoJSON để hiển thị lên Leaflet
    cac_cua_hang = serialize('geojson', CuaHang.objects.all())
    return render(request, 'home/map.html', {'data_cua_hang': cac_cua_hang})