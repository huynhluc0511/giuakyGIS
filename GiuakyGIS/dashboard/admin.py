from django.contrib import admin
from .models import Review, ReviewImage, OrderReview, Order, OrderItem, Product, Category, News, Shipper, DeliveryStatus

@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'overall_rating', 'status', 'created_at']
    list_filter = ['status', 'overall_rating', 'created_at']
    search_fields = ['order__id', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order', 'user', 'overall_rating')
        }),
        ('Đánh giá chi tiết', {
            'fields': ('food_quality', 'service_quality', 'delivery_speed', 'packaging_quality')
        }),
        ('Nội dung', {
            'fields': ('content',)
        }),
        ('Trạng thái', {
            'fields': ('status',)
        }),
        ('Phản hồi', {
            'fields': ('admin_reply', 'admin_reply_at')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'user')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'user', 'rating', 'status', 'created_at']
    list_filter = ['status', 'rating', 'created_at']
    search_fields = ['order_item__product__name', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order_item', 'user', 'rating')
        }),
        ('Nội dung', {
            'fields': ('content',)
        }),
        ('Trạng thái', {
            'fields': ('status',)
        }),
        ('Phản hồi', {
            'fields': ('admin_reply', 'admin_reply_at')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order_item', 'user', 'order_item__product')

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['review', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['review__id']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review')

# Inline cho ReviewImage
class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ['uploaded_at']

# Cập nhật ReviewAdmin để include ReviewImage
ReviewAdmin.inlines = [ReviewImageInline]


@admin.register(Shipper)
class ShipperAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'license_plate', 'vehicle_type', 'status', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'vehicle_type', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone', 'license_plate']
    readonly_fields = ['created_at', 'updated_at', 'last_location_update']
    
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('user', 'phone', 'license_plate', 'vehicle_type')
        }),
        ('Trạng thái', {
            'fields': ('status', 'is_active')
        }),
        ('Vị trí', {
            'fields': ('current_latitude', 'current_longitude', 'last_location_update'),
            'classes': ('collapse',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def get_active_deliveries_count(self, obj):
        return obj.get_active_deliveries().count()
    get_active_deliveries_count.short_description = 'Đang giao'
    
    def get_completed_today_count(self, obj):
        return obj.get_completed_deliveries_today()
    get_completed_today_count.short_description = 'Hoàn thành hôm nay'
    
    list_display = ['user', 'phone', 'license_plate', 'status', 'get_active_deliveries_count', 'get_completed_today_count']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'phone', 'status', 'total_price', 'created_at', 'shipper']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'user__username', 'full_name', 'phone']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Thông tin người dùng', {
            'fields': ('user', 'full_name', 'phone', 'address')
        }),
        ('Thông tin đơn hàng', {
            'fields': ('status', 'total_price', 'shipper', 'delivery_notes', 'estimated_delivery_time')
        }),
        ('Vị trí', {
            'fields': ('lat', 'lng'),
            'classes': ('collapse',)
        }),
        ('Thời gian', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'shipper__user')
    
    actions = ['mark_as_shipped_and_notify']
    
    def mark_as_shipped_and_notify(self, request, queryset):
        from django.utils import timezone
        from dashboard.models import DeliveryStatus
        updated_count = 0
        
        for order in queryset:
            if order.status != 'Shipped':
                # Cập nhật trạng thái đơn hàng
                order.status = 'Shipped'
                order.save()
                
                # Tạo hoặc cập nhật delivery status
                delivery, created = DeliveryStatus.objects.get_or_create(
                    order=order,
                    defaults={'status': 'pending'}
                )
                
                # Gửi thông báo cho shipper
                delivery.is_notified = True
                delivery.notification_sent_at = timezone.now()
                delivery.shipper = None  # Chưa gán shipper cụ thể
                delivery.status = 'pending'
                delivery.save()
                
                updated_count += 1
        
        self.message_user(
            request, 
            f"{updated_count} đơn hàng đã được chuyển sang trạng thái đang giao và thông báo cho tất cả shipper!", 
            messages.SUCCESS
        )
    mark_as_shipped_and_notify.short_description = "Chuyển sang đang giao & thông báo shipper"


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ['order', 'shipper', 'status', 'assigned_at', 'picked_up_at', 'delivered_at']
    list_filter = ['status', 'assigned_at', 'picked_up_at', 'delivered_at']
    search_fields = ['order__id', 'shipper__user__username', 'pickup_notes', 'delivery_notes']
    readonly_fields = ['created_at', 'assigned_at', 'picked_up_at', 'delivered_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order', 'shipper', 'status')
        }),
        ('Thời gian', {
            'fields': ('assigned_at', 'picked_up_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Ghi chú', {
            'fields': ('pickup_notes', 'delivery_notes', 'failure_reason')
        }),
        ('Bằng chứng', {
            'fields': ('pickup_photo', 'delivery_photo', 'customer_signature')
        }),
        ('Đánh giá từ shipper', {
            'fields': ('shipper_rating', 'shipper_notes')
        }),
        ('Thời gian', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'shipper__user')
    
    actions = ['mark_as_picked_up', 'mark_as_delivered', 'mark_as_failed', 'mark_as_shipped_and_notify']
    
    def mark_as_picked_up(self, request, queryset):
        for delivery in queryset.filter(status='pending'):
            delivery.update_status('picked_up')
        self.message_user(request, f"Đã cập nhật {queryset.count()} giao hàng thành 'Đã lấy hàng'")
    mark_as_picked_up.short_description = "Đánh dấu là 'Đã lấy hàng'"
    
    def mark_as_delivered(self, request, queryset):
        for delivery in queryset.filter(status__in=['picked_up', 'delivering']):
            delivery.update_status('delivered')
        self.message_user(request, f"Đã cập nhật {queryset.count()} giao hàng thành 'Đã giao hàng'")
    mark_as_delivered.short_description = "Đánh dấu là 'Đã giao hàng'"
    
    def mark_as_failed(self, request, queryset):
        for delivery in queryset.filter(status__in=['picked_up', 'delivering']):
            delivery.update_status('failed', notes="Admin đánh dấu thất bại")
        self.message_user(request, f"Đã cập nhật {queryset.count()} giao hàng thành 'Thất bại'")
    mark_as_failed.short_description = "Đánh dấu là 'Thất bại'"
