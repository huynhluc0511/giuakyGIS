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

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người dùng")
    full_name = models.CharField(max_length=200, verbose_name="Họ tên người nhận")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ giao hàng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Trạng thái")
    total_price = models.FloatField(default=0, verbose_name="Tổng tiền")
    
    # Các trường GIS cho vị trí người dùng
    lat = models.FloatField(null=True, blank=True, verbose_name="Vĩ độ người dùng")
    lng = models.FloatField(null=True, blank=True, verbose_name="Kinh độ người dùng")
    
    # Thông tin giao hàng
    shipper = models.ForeignKey('Shipper', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', verbose_name="Shipper giao hàng")
    delivery_notes = models.TextField(blank=True, verbose_name="Ghi chú giao hàng")
    estimated_delivery_time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian giao hàng dự kiến")

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

    @property
    def total_price(self):
        return self.quantity * self.price

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


# 11. Giới thiệu - Bài viết trang giới thiệu
class About(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Bản nháp'),
        ('published', 'Đã xuất bản'),
        ('archived', 'Lưu trữ'),
    )
    
    title = models.CharField(max_length=200, verbose_name="Tiêu đề bài viết")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Nội dung bài viết")
    excerpt = models.TextField(max_length=300, blank=True, verbose_name="Tóm tắt")
    featured_image = models.ImageField(upload_to='about/', null=True, blank=True, verbose_name="Hình ảnh nổi bật")
    external_link = models.URLField(blank=True, verbose_name="Liên kết bài viết bên ngoài")
    source_type = models.CharField(
        max_length=20, 
        choices=[
            ('manual', 'Tự viết'),
            ('word', 'Từ Word'),
            ('external', 'Từ liên kết')
        ], 
        default='manual', 
        verbose_name="Nguồn bài viết"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Tác giả")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Bài viết trang giới thiệu"
        ordering = ['order', '-created_at']


# 12. Thông tin cá nhân người dùng
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Người dùng")
    
    # Basic Information
    phone = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Ảnh đại diện")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Nam'),
            ('female', 'Nữ'),
            ('other', 'Khác'),
        ],
        blank=True,
        verbose_name="Giới tính"
    )
    
    # Extended Information
    bio = models.TextField(max_length=500, blank=True, verbose_name="Tiểu sử")
    website = models.URLField(blank=True, verbose_name="Website cá nhân")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    instagram = models.URLField(blank=True, verbose_name="Instagram")
    twitter = models.URLField(blank=True, verbose_name="Twitter")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    
    # Status and Verification
    is_verified = models.BooleanField(default=False, verbose_name="Đã xác thực")
    is_premium = models.BooleanField(default=False, verbose_name="Người dùng VIP")
    loyalty_points = models.IntegerField(default=0, verbose_name="Điểm tích lũy")
    
    # Preferences
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('vi', 'Tiếng Việt'),
            ('en', 'English'),
        ],
        default='vi',
        verbose_name="Ngôn ngữ ưu tiên"
    )
    email_notifications = models.BooleanField(default=True, verbose_name="Thông báo email")
    sms_notifications = models.BooleanField(default=False, verbose_name="Thông báo SMS")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP đăng nhập cuối")
    
    def __str__(self):
        return f"Profile của {self.user.username}"

    class Meta:
        verbose_name = "Thông tin người dùng"
        verbose_name_plural = "Thông tin người dùng"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]

    @property
    def full_name(self):
        """Get full name of the user"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def display_name(self):
        """Get display name for UI"""
        return self.user.first_name or self.user.username

    @property
    def age(self):
        """Calculate age from birth date"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def social_links(self):
        """Get all social media links as dictionary"""
        return {
            'website': self.website,
            'facebook': self.facebook,
            'instagram': self.instagram,
            'twitter': self.twitter,
            'linkedin': self.linkedin
        }

    def update_last_login_ip(self, ip_address):
        """Update last login IP address"""
        self.last_login_ip = ip_address
        self.save(update_fields=['last_login_ip'])

    def add_loyalty_points(self, points):
        """Add loyalty points to customer"""
        self.loyalty_points += points
        self.save(update_fields=['loyalty_points'])

    def get_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            self.phone, self.address, self.avatar, self.birth_date, self.gender,
            self.bio, self.website, self.facebook, self.instagram, self.twitter, self.linkedin
        ]
        filled_fields = sum(1 for field in fields if field)
        return round((filled_fields / len(fields)) * 100, 1)


# 6. Tin tức (News)
class News(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Bản nháp'),
        ('published', 'Đã xuất bản'),
        ('archived', 'Đã lưu trữ'),
    )

    CATEGORY_CHOICES = (
        ('promotion', 'Khuyến mãi'),
        ('event', 'Sự kiện'),
        ('product', 'Sản phẩm mới'),
        ('company', 'Tin công ty'),
        ('other', 'Khác'),
    )

    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    slug = models.SlugField(unique=True, max_length=255, verbose_name="Slug")
    summary = models.TextField(max_length=500, blank=True, verbose_name="Tóm tắt")
    content = models.TextField(verbose_name="Nội dung")
    image = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name="Hình ảnh")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Danh mục")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    is_featured = models.BooleanField(default=False, verbose_name="Tin nổi bật")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tác giả")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xuất bản")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    meta_description = models.CharField(max_length=255, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Tin tức"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['created_at']),
            models.Index(fields=['published_at']),
        ]

    @property
    def is_published(self):
        """Check if news is published"""
        return self.status == 'published'

    @property
    def display_category(self):
        """Get display name for category"""
        category_map = dict(self.CATEGORY_CHOICES)
        return category_map.get(self.category, self.category)

    @property
    def display_status(self):
        """Get display name for status"""
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, self.status)

    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


# 7. Đánh giá sản phẩm (Reviews)
class Review(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    )
    
    # Mỗi đánh giá gắn với 1 OrderItem (1 món trong đơn hàng)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='reviews', verbose_name="Món trong đơn hàng")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Người dùng")
    
    # Điểm đánh giá (1-5 sao)
    rating = models.IntegerField(verbose_name="Điểm đánh giá", choices=[(i, f"{i} sao") for i in range(1, 6)])
    
    # Nội dung đánh giá
    content = models.TextField(verbose_name="Nội dung đánh giá")
    
    # Trạng thái duyệt
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đánh giá")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    
    # Phản hồi từ admin
    admin_reply = models.TextField(blank=True, verbose_name="Phản hồi của cửa hàng")
    admin_reply_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày phản hồi")
    
    class Meta:
        verbose_name_plural = "Đánh giá"
        # Ràng buộc: Mỗi user chỉ được đánh giá 1 lần cho mỗi order_item
        unique_together = ['order_item', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'order_item']),
            models.Index(fields=['status']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Đánh giá #{self.id} - {self.user.username} - {self.order_item.product.name} ({self.rating} sao)"
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def display_status(self):
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, self.status)


# 8. Hình ảnh đánh giá
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', verbose_name="Đánh giá")
    image = models.ImageField(upload_to='reviews/', verbose_name="Hình ảnh")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")
    
    class Meta:
        verbose_name_plural = "Hình ảnh đánh giá"
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Ảnh đánh giá #{self.id} - {self.review.id}"


# 9. Đánh giá đơn hàng (OrderReview)
class OrderReview(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    )
    
    # Đánh giá gắn với 1 đơn hàng
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_reviews', verbose_name="Đơn hàng")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_reviews', verbose_name="Người dùng")
    
    # Điểm đánh giá tổng thể (1-5 sao)
    overall_rating = models.IntegerField(verbose_name="Đánh giá tổng thể", choices=[(i, f"{i} sao") for i in range(1, 6)])
    
    # Đánh giá chi tiết
    food_quality = models.IntegerField(verbose_name="Chất lượng món ăn", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    service_quality = models.IntegerField(verbose_name="Chất lượng dịch vụ", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    delivery_speed = models.IntegerField(verbose_name="Tốc độ giao hàng", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    packaging_quality = models.IntegerField(verbose_name="Chất lượng đóng gói", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    
    # Nội dung đánh giá
    content = models.TextField(verbose_name="Nội dung đánh giá", blank=True)
    
    # Trạng thái duyệt
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đánh giá")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    
    # Phản hồi từ admin
    admin_reply = models.TextField(blank=True, verbose_name="Phản hồi của cửa hàng")
    admin_reply_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày phản hồi")
    
    class Meta:
        verbose_name_plural = "Đánh giá đơn hàng"
        # Ràng buộc: Mỗi user chỉ được đánh giá 1 lần cho mỗi đơn hàng
        unique_together = ['order', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'user']),
            models.Index(fields=['status']),
            models.Index(fields=['overall_rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Đánh giá đơn hàng #{self.order.id} - {self.user.username} ({self.overall_rating} sao)"
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def display_status(self):
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, self.status)
    
    def can_review(self):
        """Kiểm tra xem đơn hàng có thể đánh giá được không (chỉ khi đã giao hàng)"""
        return self.order.status == 'Delivered'
    
    def get_average_rating(self):
        """Tính điểm trung bình của các tiêu chí chi tiết"""
        ratings = []
        if self.food_quality:
            ratings.append(self.food_quality)
        if self.service_quality:
            ratings.append(self.service_quality)
        if self.delivery_speed:
            ratings.append(self.delivery_speed)
        if self.packaging_quality:
            ratings.append(self.packaging_quality)
        
        if ratings:
            return sum(ratings) / len(ratings)
        return self.overall_rating


# 10. Shipper (Người giao hàng)
class Shipper(models.Model):
    STATUS_CHOICES = (
        ('available', 'Sẵn sàng'),
        ('busy', 'Bận'),
        ('offline', 'Ngoại tuyến'),
    )
    
    # Thông tin cơ bản
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shipper_profile', verbose_name="Tài khoản")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    license_plate = models.CharField(max_length=20, unique=True, verbose_name="Biển số xe")
    vehicle_type = models.CharField(max_length=50, verbose_name="Loại xe")
    
    # Trạng thái
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Trạng thái")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    
    # Thông tin vị trí
    current_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Vĩ độ hiện tại")
    current_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Kinh độ hiện tại")
    last_location_update = models.DateTimeField(null=True, blank=True, verbose_name="Cập nhật vị trí lần cuối")
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    
    class Meta:
        verbose_name_plural = "Shipper"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['license_plate']),
            models.Index(fields=['last_location_update']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.license_plate}"
    
    @property
    def display_status(self):
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, self.status)
    
    def get_active_deliveries(self):
        """Lấy các đơn hàng đang giao"""
        return self.deliveries.filter(status__in=['picked_up', 'delivering'])
    
    def get_completed_deliveries_today(self):
        """Lấy số đơn hàng đã hoàn thành hôm nay"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.deliveries.filter(
            status='delivered',
            delivered_at__date=today
        ).count()
    
    def update_location(self, lat, lng):
        """Cập nhật vị trí hiện tại của shipper"""
        self.current_latitude = lat
        self.current_longitude = lng
        self.last_location_update = timezone.now()
        self.save()


# 11. Delivery Status (Trạng thái giao hàng)
class DeliveryStatus(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ nhận hàng'),
        ('picked_up', 'Đã lấy hàng'),
        ('delivering', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('failed', 'Giao hàng thất bại'),
        ('cancelled', 'Đã hủy'),
    )
    
    # Liên kết
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery', verbose_name="Đơn hàng")
    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', verbose_name="Shipper")
    
    # Trạng thái
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái giao hàng")
    is_notified = models.BooleanField(default=False, verbose_name="Đã thông báo cho shipper")
    notification_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian gửi thông báo")
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    # Thời gian quan trọng
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian giao cho shipper")
    picked_up_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian lấy hàng")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian giao hàng")
    
    # Ghi chú
    pickup_notes = models.TextField(blank=True, verbose_name="Ghi chú lấy hàng")
    delivery_notes = models.TextField(blank=True, verbose_name="Ghi chú giao hàng")
    failure_reason = models.TextField(blank=True, verbose_name="Lý do thất bại")
    
    # Bằng chứng
    pickup_photo = models.ImageField(upload_to='delivery/pickup/', null=True, blank=True, verbose_name="Ảnh lấy hàng")
    delivery_photo = models.ImageField(upload_to='delivery/delivery/', null=True, blank=True, verbose_name="Ảnh giao hàng")
    customer_signature = models.ImageField(upload_to='delivery/signature/', null=True, blank=True, verbose_name="Chữ ký người dùng")
    
    # Đánh giá từ shipper
    shipper_rating = models.IntegerField(null=True, blank=True, verbose_name="Đánh giá của shipper", 
                                       choices=[(i, f"{i} sao") for i in range(1, 6)])
    shipper_notes = models.TextField(blank=True, verbose_name="Ghi chú của shipper")
    
    class Meta:
        verbose_name_plural = "Trạng thái giao hàng"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'shipper']),
            models.Index(fields=['order']),
            models.Index(fields=['assigned_at']),
            models.Index(fields=['delivered_at']),
        ]
    
    def __str__(self):
        return f"Giao hàng #{self.order.id} - {self.get_status_display()}"
    
    @property
    def display_status(self):
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, self.status)
    
    def can_update_status(self, new_status):
        """Kiểm tra xem có thể cập nhật trạng thái không"""
        status_flow = {
            'pending': ['picked_up', 'cancelled'],
            'picked_up': ['delivering', 'failed', 'cancelled'],
            'delivering': ['delivered', 'failed', 'cancelled'],
            'delivered': [],  # Final state
            'failed': ['picked_up', 'cancelled'],  # Can retry or cancel
            'cancelled': [],  # Final state
        }
        return new_status in status_flow.get(self.status, [])
    
    def update_status(self, new_status, notes="", photo=None):
        """Cập nhật trạng thái giao hàng"""
        if not self.can_update_status(new_status):
            raise ValueError(f"Không thể chuyển từ {self.status} sang {new_status}")
        
        old_status = self.status
        self.status = new_status
        
        # Cập nhật thời gian tương ứng
        from django.utils import timezone
        now = timezone.now()
        
        if new_status == 'picked_up' and not self.picked_up_at:
            self.picked_up_at = now
            if notes:
                self.pickup_notes = notes
            if photo:
                self.pickup_photo = photo
                
        elif new_status == 'delivered' and not self.delivered_at:
            self.delivered_at = now
            if notes:
                self.delivery_notes = notes
            if photo:
                self.delivery_photo = photo
            # Cập nhật trạng thái đơn hàng
            self.order.status = 'Delivered'
            self.order.save()
            
        elif new_status == 'failed':
            if notes:
                self.failure_reason = notes
                
        elif new_status == 'cancelled':
            # Có thể cần cập nhật lại trạng thái đơn hàng
            if old_status in ['picked_up', 'delivering']:
                self.order.status = 'Processing'  # Hoặc trạng thái phù hợp khác
                self.order.save()
        
        self.save()
        
        # Gửi notification cho người dùng (nếu cần)
        if new_status in ['picked_up', 'delivering', 'delivered']:
            self.send_customer_notification(new_status)
    
    def send_customer_notification(self, status):
        """Gửi thông báo cho người dùng (placeholder)"""
        # TODO: Implement notification system
        pass
    
    def get_delivery_duration(self):
        """Tính thời gian giao hàng"""
        if self.picked_up_at and self.delivered_at:
            return self.delivered_at - self.picked_up_at
        return None