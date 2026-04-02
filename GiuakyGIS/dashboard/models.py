from django.db import models
from django.contrib.auth.models import User

# 1. Danh mục món ăn
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Danh mục"

# 2. Sản phẩm thức ăn
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    name = models.CharField(max_length=200, verbose_name="Tên món ăn")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    price = models.FloatField(verbose_name="Giá tiền")
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh")
    is_available = models.BooleanField(default=True, verbose_name="Còn hàng")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Sản phẩm"

# 3. Đơn hàng (Đã gộp lat/lng vào đây)
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Đang chờ xử lý'),
        ('Processing', 'Đang chế biến'),
        ('Shipped', 'Đang giao hàng'),
        ('Delivered', 'Đã giao hàng'),
        ('Cancelled', 'Đã hủy'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Khách hàng")
    full_name = models.CharField(max_length=200, verbose_name="Họ tên người nhận")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ giao hàng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Trạng thái")
    total_price = models.FloatField(default=0, verbose_name="Tổng tiền")
    
    # Các trường GIS cho vị trí khách hàng
    lat = models.FloatField(null=True, blank=True, verbose_name="Vĩ độ khách hàng")
    lng = models.FloatField(null=True, blank=True, verbose_name="Kinh độ khách hàng")

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"

    class Meta:
        verbose_name_plural = "Đơn hàng"

# 4. Chi tiết từng món trong đơn hàng
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, verbose_name="Số lượng")
    price = models.FloatField(verbose_name="Giá lúc mua")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# 5. Cửa hàng (Được đưa ra ngoài làm class riêng biệt)
class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên cửa hàng")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ cửa hàng")
    latitude = models.FloatField(verbose_name="Vĩ độ")
    longitude = models.FloatField(verbose_name="Kinh độ")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cửa hàng"