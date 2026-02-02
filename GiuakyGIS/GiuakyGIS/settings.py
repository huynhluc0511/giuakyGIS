import os
import sys
from pathlib import Path

# 1. BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY & DEBUG
SECRET_KEY = 'django-insecure-xexetig6k^y0d7%t7l*+qemj+hyng07cn@xa3-_q@hfo38=-u@'
DEBUG = True
ALLOWED_HOSTS = []

# 3. APPLICATION DEFINITION
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # BẮT BUỘC phải có dòng này để dùng GIS
    'home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GiuakyGIS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'GiuakyGIS.wsgi.application'

# 4. DATABASE
DATABASES = {
    'default': {
        # Nếu bạn dùng GIS, thường sẽ dùng 'django.contrib.gis.db.backends.postgis'
        # Nhưng nếu chỉ học tập với SQLite thì dùng engine mặc định:
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 5. PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 6. INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 7. STATIC FILES
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 8. CẤU HÌNH GDAL CHO WINDOWS (PHẦN QUAN TRỌNG NHẤT)
if os.name == 'nt':
    # Đường dẫn gốc của OSGeo4W
    OSGEO4W_DIR = r"C:\OSGeo4W"
    
    if os.path.exists(OSGEO4W_DIR):
        # Thiết lập biến môi trường
        os.environ['OSGEO4W_ROOT'] = OSGEO4W_DIR
        os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_DIR, r"share\gdal")
        os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_DIR, r"share\proj")
        os.environ['PATH'] = os.path.join(OSGEO4W_DIR, "bin") + ";" + os.environ['PATH']
        
        # CHÚ Ý: Kiểm tra file dll trong C:\OSGeo4W\bin
        # Nếu không thấy gdal308.dll, hãy đổi tên bên dưới thành gdal309.dll hoặc gdal310.dll...
        GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_DIR, r"bin\gdal308.dll")
    else:
        print("Cảnh báo: Không tìm thấy thư mục C:\OSGeo4W. Vui lòng cài đặt OSGeo4W.")