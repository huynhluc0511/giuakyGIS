from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import SanPham, CuaHang

admin.site.register(SanPham)

# Dùng GISModelAdmin để hiện bản đồ khi thêm Cửa hàng
@admin.register(CuaHang)
class CuaHangAdmin(GISModelAdmin):
    list_display = ('ten_cua_hang', 'vi_tri')