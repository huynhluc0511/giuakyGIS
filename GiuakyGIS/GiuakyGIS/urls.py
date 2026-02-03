
from django.contrib import admin

from django.urls import path, include # Nhớ import thêm include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Trỏ tất cả đường dẫn gốc vào app home
    path('', include('home.urls')), 

from django.urls import path
from home import views as home
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home.home, name='home'),
>>>>>>> fc259ba56672ee8040c2f77923d0480bd95047d6
]
import os

# Cấu hình đường dẫn file Tĩnh (CSS/JS)
STATIC_URL = 'static/'

# Cấu hình đường dẫn file Media (Ảnh món ăn upload lên)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')