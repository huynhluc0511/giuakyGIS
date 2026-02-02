
from django.contrib import admin
from django.urls import path, include # Nhớ import thêm include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Trỏ tất cả đường dẫn gốc vào app home
    path('', include('home.urls')), 
]
import os

# Cấu hình đường dẫn file Tĩnh (CSS/JS)
STATIC_URL = 'static/'

# Cấu hình đường dẫn file Media (Ảnh món ăn upload lên)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')