from django.contrib import admin
from django.utils.html import format_html
from .models import OrderReview, ReviewImage, ReviewReply, ReviewHelpful

@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'rating_display', 'comment_preview', 'is_recommended', 'is_public', 'created_at']
    list_filter = ['rating', 'is_recommended', 'is_public', 'created_at']
    search_fields = ['user__username', 'order__id', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'rating_display']
    list_per_page = 20
    ordering = ['-created_at']
    
    def order_id(self, obj):
        return f'#{obj.order.id}'
    order_id.short_description = 'Đơn hàng'
    
    def rating_display(self, obj):
        stars = ''
        for i in range(1, 6):
            if i <= obj.rating:
                stars += '⭐'
            else:
                stars += '☆'
        return format_html('<span style="font-size: 1.2em;">{}</span>', stars)
    rating_display.short_description = 'Đánh giá'
    
    def comment_preview(self, obj):
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return '-'
    comment_preview.short_description = 'Bình luận'
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order', 'user', 'rating', 'is_recommended')
        }),
        ('Nội dung đánh giá', {
            'fields': ('comment', 'is_public')
        }),
        ('Thông tin hệ thống', {
            'fields': ('rating_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['review_info', 'image_preview', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['review__order__id', 'review__user__username', 'caption']
    readonly_fields = ['uploaded_at', 'image_preview']
    
    def review_info(self, obj):
        return f'Đơn #{obj.review.order.id} - {obj.review.user.username}'
    review_info.short_description = 'Đánh giá'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Ảnh xem trước'

@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ['review_info', 'content_preview', 'replied_by', 'replied_at']
    list_filter = ['replied_at']
    search_fields = ['review__order__id', 'review__user__username', 'content']
    readonly_fields = ['replied_at']
    
    def review_info(self, obj):
        return f'Đơn #{obj.review.order.id} - {obj.review.user.username}'
    review_info.short_description = 'Đánh giá'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Nội dung trả lời'

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review_info', 'user', 'is_helpful_display', 'voted_at']
    list_filter = ['is_helpful', 'voted_at']
    search_fields = ['review__order__id', 'review__user__username', 'user__username']
    readonly_fields = ['voted_at']
    
    def review_info(self, obj):
        return f'Đơn #{obj.review.order.id} - {obj.review.user.username}'
    review_info.short_description = 'Đánh giá'
    
    def is_helpful_display(self, obj):
        return format_html('<span style="color: {};">{}</span>', 
                          'green' if obj.is_helpful else 'red',
                          'Hữu ích' if obj.is_helpful else 'Không hữu ích')
    is_helpful_display.short_description = 'Loại bình chọn'

# Custom admin site header
admin.site.site_header = 'FastFood Universe - Quản lý Đánh giá'
admin.site.site_title = 'Admin Đánh giá'
admin.site.index_title = 'Chào mừng đến trang quản lý đánh giá FastFood Universe'
