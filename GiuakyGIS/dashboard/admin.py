from django.contrib import admin
from .models import Review, ReviewImage, OrderReview, Order, OrderItem, Product, Category, News

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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'phone', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'user__username', 'full_name', 'phone']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Thông tin người dùng', {
            'fields': ('user', 'full_name', 'phone', 'address')
        }),
        ('Thông tin đơn hàng', {
            'fields': ('status', 'total_price')
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
        return super().get_queryset(request).select_related('user')

