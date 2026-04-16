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
    opening_hours = models.CharField(max_length=255, verbose_name="Giờ mở cửa", default="9:00 - 22:00", blank=True)
    warehouse_info = models.TextField(verbose_name="Thông tin quản lý kho", blank=True, default="")

    def __str__(self):
        return self.name

# 6. Quản Lý Kho
class Warehouse(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='warehouse', verbose_name="Cửa hàng")
    info = models.TextField(verbose_name="Thông tin quản lý kho", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"Kho - {self.store.name}"

    class Meta:
        verbose_name_plural = "Quản Lý Kho"

# 7. Sản phẩm trong kho
class WarehouseItem(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items', verbose_name="Kho")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity = models.IntegerField(default=0, verbose_name="Số lượng tồn")
    unit = models.CharField(max_length=50, default="cái", verbose_name="Đơn vị")
    min_quantity = models.IntegerField(default=10, verbose_name="Tồn kho tối thiểu")
    unit_price = models.FloatField(default=0, verbose_name="Giá nhập")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit}"

    class Meta:
        verbose_name_plural = "Sản Phẩm Kho"

# 8. Giao dịch kho (nhập/xuất)
class WarehouseTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('import', 'Nhập hàng'),
        ('export', 'Xuất hàng'),
    )
    
    warehouse_item = models.ForeignKey(WarehouseItem, on_delete=models.CASCADE, related_name='transactions', verbose_name="Sản phẩm kho")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Loại giao dịch")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.FloatField(default=0, verbose_name="Đơn giá")
    supplier = models.CharField(max_length=255, blank=True, verbose_name="Nhà cung ứng")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giao dịch")

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.warehouse_item.product.name}"

    class Meta:
        verbose_name_plural = "Giao Dịch Kho"
        ordering = ['-created_at']


# 9. Phiếu nhập/xuất kho (Batch) - để nhóm nhiều giao dịch
class WarehouseBatch(models.Model):
    BATCH_TYPES = (
        ('import', 'Nhập hàng'),
        ('export', 'Xuất hàng'),
    )
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='batches', verbose_name="Kho")
    batch_type = models.CharField(max_length=20, choices=BATCH_TYPES, verbose_name="Loại phiếu")
    batch_number = models.CharField(max_length=50, unique=True, verbose_name="Số phiếu")
    supplier = models.CharField(max_length=255, blank=True, verbose_name="Nhà cung ứng/Người nhận")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    total_amount = models.FloatField(default=0, verbose_name="Tổng tiền")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Lần cập nhật cuối")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Người tạo")
    is_printed = models.BooleanField(default=False, verbose_name="Đã in")
    printed_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian in")

    def __str__(self):
        return f"{self.batch_number} - {self.get_batch_type_display()}"

    class Meta:
        verbose_name_plural = "Phiếu Nhập/Xuất Kho"
        ordering = ['-created_at']

    def calculate_total(self):
        """Tính tổng tiền của phiếu"""
        total = sum(item.quantity * item.unit_price for item in self.items.all())
        self.total_amount = total
        return total


# 10. Chi tiết phiếu nhập/xuất kho
class WarehouseBatchItem(models.Model):
    batch = models.ForeignKey(WarehouseBatch, on_delete=models.CASCADE, related_name='items', verbose_name="Phiếu")
    warehouse_item = models.ForeignKey(WarehouseItem, on_delete=models.CASCADE, verbose_name="Sản phẩm kho")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.FloatField(verbose_name="Đơn giá")

    def __str__(self):
        return f"{self.warehouse_item.product.name} - {self.quantity}"

    class Meta:
        verbose_name_plural = "Chi Tiết Phiếu Nhập/Xuất"