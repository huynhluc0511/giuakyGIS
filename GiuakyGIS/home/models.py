from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Order
import uuid
import os

def get_review_image_path(instance, filename):
    """Generate upload path for review images"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('review_images', filename)

class OrderReview(models.Model):
    """Model for order reviews"""
    RATING_CHOICES = [
        (1, '1 sao - Rất không hài lòng'),
        (2, '2 sao - Không hài lòng'),
        (3, '3 sao - Bình thường'),
        (4, '4 sao - Hài lòng'),
        (5, '5 sao - Rất hài lòng'),
    ]
    
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='order_review',
        verbose_name='Đơn hàng'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Khách hàng'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES, 
        default=5,
        verbose_name='Đánh giá sao'
    )
    comment = models.TextField(
        blank=True, 
        verbose_name='Bình luận'
    )
    is_recommended = models.BooleanField(
        default=True, 
        verbose_name='Có推荐 không?'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Ngày tạo'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Ngày cập nhật'
    )
    is_public = models.BooleanField(
        default=True, 
        verbose_name='Hiển thị công khai'
    )
    
    class Meta:
        verbose_name = 'Đánh giá đơn hàng'
        verbose_name_plural = 'Đánh giá đơn hàng'
        ordering = ['-created_at']
        unique_together = ['order', 'user']  # Mỗi đơn hàng chỉ được đánh giá 1 lần
    
    def __str__(self):
        return f'Đánh giá đơn #{self.order.id} - {self.user.username}'
    
    @property
    def rating_stars(self):
        """Return star display HTML"""
        stars = ''
        for i in range(1, 6):
            if i <= self.rating:
                stars += '⭐'
            else:
                stars += '☆'
        return stars

class ReviewImage(models.Model):
    """Model for review images"""
    review = models.ForeignKey(
        OrderReview, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Đánh giá'
    )
    image = models.ImageField(
        upload_to=get_review_image_path, 
        verbose_name='Ảnh đánh giá'
    )
    caption = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Tiêu đề ảnh'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Ngày tải lên'
    )
    
    class Meta:
        verbose_name = 'Ảnh đánh giá'
        verbose_name_plural = 'Ảnh đánh giá'
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f'Ảnh của đánh giá #{self.review.id}'

class ReviewReply(models.Model):
    """Model for admin/shop replies to reviews"""
    review = models.OneToOneField(
        OrderReview, 
        on_delete=models.CASCADE, 
        related_name='reply',
        verbose_name='Đánh giá'
    )
    content = models.TextField(
        verbose_name='Nội dung trả lời'
    )
    replied_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_staff': True},
        verbose_name='Người trả lời'
    )
    replied_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Ngày trả lời'
    )
    
    class Meta:
        verbose_name = 'Trả lời đánh giá'
        verbose_name_plural = 'Trả lời đánh giá'
    
    def __str__(self):
        return f'Trả lời đánh giá #{self.review.id}'

class ReviewHelpful(models.Model):
    """Model for helpful votes on reviews"""
    review = models.ForeignKey(
        OrderReview, 
        on_delete=models.CASCADE, 
        related_name='helpful_votes',
        verbose_name='Đánh giá'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Người bình chọn'
    )
    is_helpful = models.BooleanField(
        default=True, 
        verbose_name='Hữu ích'
    )
    voted_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Ngày bình chọn'
    )
    
    class Meta:
        verbose_name = 'Bình chọn hữu ích'
        verbose_name_plural = 'Bình chọn hữu ích'
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f'{self.user.username} {"hữu ích" if self.is_helpful else "không hữu ích"} đánh giá #{self.review.id}'
