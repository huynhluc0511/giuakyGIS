from django.db import models
from django.contrib.gis.db import models as gis_models # Import thư viện GIS

# 1. Bảng Sản phẩm (Đồ ăn)
class SanPham(models.Model):
    ten_mon = models.CharField(max_length=200, verbose_name="Tên món")
    gia = models.IntegerField(verbose_name="Giá bán")
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả")
    hinh_anh = models.ImageField(upload_to='food_images/', blank=True)

    def __str__(self):
        return self.ten_mon

# 2. Bảng Cửa hàng (Chứa dữ liệu GIS - Toạ độ)
class CuaHang(models.Model):
    ten_cua_hang = models.CharField(max_length=100)
    dia_chi = models.CharField(max_length=255)
    
    # Đây là trường quan trọng nhất: PointField lưu kinh độ/vĩ độ
    vi_tri = gis_models.PointField(srid=4326, help_text="Vị trí trên bản đồ") 

    def __str__(self):
        return self.ten_cua_hang
# Create your models here.
