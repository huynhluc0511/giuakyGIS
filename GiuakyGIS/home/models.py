from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. Thực đơn (Cập nhật từ Sản phẩm)
class ThucDon(models.Model):
    DANH_MUC = [
        ('hamburger', 'Hamburger'),
        ('pizza', 'Pizza'),
        ('ga_chien', 'Gà chiên'),
        ('do_uong', 'Đồ uống'),
        ('khoai_tay', 'Khoai tây chiên'),
    ]
    ten_mon = models.CharField(max_length=255, verbose_name="Tên món ăn")
    phan_loai = models.CharField(max_length=50, choices=DANH_MUC, default='hamburger')
    gia = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá")
    don_vi = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đơn vị")
    mo_ta = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    hinh_anh = models.ImageField(upload_to='menu/', null=True, blank=True)
    trang_thai = models.BooleanField(default=True, verbose_name="Còn hàng")

    def __str__(self):
        return f"[{self.get_phan_loai_display()}] {self.ten_mon}"

# 2. Kho hàng
class KhoHang(models.Model):
    thuc_don = models.OneToOneField(ThucDon, on_delete=models.CASCADE, related_name='kho')
    so_luong_ton = models.IntegerField(default=0, verbose_name="Số lượng tồn")
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

# 3. Giỏ hàng
class GioHang(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mon_an = models.ForeignKey(ThucDon, on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField(default=1)
    ngay_them = models.DateTimeField(auto_now_add=True)

    def tam_tinh(self):
        return self.so_luong * self.mon_an.gia

# 4. Liên hệ
class LienHe(models.Model):
    ho_ten = models.CharField(max_length=255)
    email = models.EmailField()
    chu_de = models.CharField(max_length=255)
    noi_dung = models.TextField()
    ngay_gui = models.DateTimeField(auto_now_add=True)

# 5. Shipper (Giữ nguyên)
class Shipper(models.Model):
    ho_ten = models.CharField(max_length=255)
    so_dien_thoai = models.CharField(max_length=20)
    trang_thai = models.CharField(max_length=50, default='rảnh')

    def __str__(self):
        return self.ho_ten

# 6. Đơn hàng (Giữ nguyên)
class DonHang(models.Model):
    TRANG_THAI_CHOICES = [
        ('Chưa giao', 'Chưa giao'),
        ('Đang giao', 'Đang giao'),
        ('Đã giao', 'Đã giao'),
    ]
    khach_hang = models.ForeignKey(User, on_delete=models.CASCADE)
    dia_chi_giao = models.TextField()
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='Chưa giao')
    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, blank=True)
    tong_tien = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ngay_tao = models.DateTimeField(auto_now_add=True)

# 7. Chi tiết đơn hàng (Giữ nguyên)
class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE, related_name='chi_tiet')
    thuc_don = models.ForeignKey(ThucDon, on_delete=models.CASCADE)
    so_luong = models.IntegerField()
    don_gia = models.DecimalField(max_digits=12, decimal_places=2)

# 8. Lộ trình Shipper (Dữ liệu GIS cho map.html - Giữ nguyên)
class LoTrinhShipper(models.Model):
    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE)
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    thoi_gian = models.DateTimeField(auto_now_add=True)