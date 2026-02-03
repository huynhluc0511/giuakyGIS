from django.db import models

# 1. Sản phẩm (Bao gồm các loại món ăn)
class SanPham(models.Model):
    LOAI_MON_AN = [
        ('hamburger', 'Hamburger'),
        ('pizza', 'Pizza'),
        ('ga_chien', 'Gà chiên'),
        ('do_uong', 'Đồ uống'),
        ('khoai_tay', 'Khoai tây'),
    ]
    ten_san_pham = models.CharField(max_length=255)
    phan_loai = models.CharField(max_length=50, choices=LOAI_MON_AN, default='hamburger')
    gia = models.DecimalField(max_digits=12, decimal_places=2)
    don_vi = models.CharField(max_length=50, default='phần')
    mo_ta = models.TextField(null=True, blank=True)
    trang_thai = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_phan_loai_display()}] {self.ten_san_pham}"

# 2. Kho hàng
class KhoHang(models.Model):
    san_pham = models.OneToOneField(SanPham, on_delete=models.CASCADE)
    so_luong = models.IntegerField(default=0)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

# 3. Nhập/Xuất hàng (Quản lý biến động kho)
class GiaoDichKho(models.Model):
    LOAI_GD = [('nhap', 'Nhập'), ('xuat', 'Xuất')]
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    loai = models.CharField(max_length=10, choices=LOAI_GD)
    so_luong = models.IntegerField()
    ngay_tao = models.DateTimeField(auto_now_add=True)

# 4. Shipper
class Shipper(models.Model):
    ho_ten = models.CharField(max_length=255)
    so_dien_thoai = models.CharField(max_length=20)
    trang_thai = models.CharField(max_length=50, default='rảnh') # rảnh, đang giao

# 5. Đơn hàng
class DonHang(models.Model):
    khach_hang = models.CharField(max_length=255)
    dia_chi_giao = models.TextField()
    trang_thai = models.CharField(max_length=50, default='Chưa giao')
    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

# 6. Chi tiết đơn hàng
class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE, related_name='chi_tiet')
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    so_luong = models.IntegerField()
    don_gia = models.DecimalField(max_digits=12, decimal_places=2)

# 7. Lộ trình Shipper (Dành cho trang map.html)
class LoTrinhShipper(models.Model):
    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE)
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    thoi_gian = models.DateTimeField(auto_now_add=True)