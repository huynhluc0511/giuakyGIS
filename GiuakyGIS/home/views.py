from django.shortcuts import render

# --- Trang chủ ---
def home_view(request):
    return render(request, 'home.html')

# --- Nhóm thực đơn (Menu) ---
def do_uong_view(request):
    return render(request, 'do-uong.html')

def ga_chien_view(request):
    return render(request, 'ga-chien.html')

def hamburger_view(request):
    return render(request, 'hamburger.html')

def khoai_tay_view(request):
    return render(request, 'khoai-tay.html')

def pizza_view(request):
    return render(request, 'pizza.html')

# --- Nhóm chức năng & Tiện ích ---
def gio_hang_view(request):
    # Django phân biệt hoa thường, file của bạn là 'Gio-hang.html'
    return render(request, 'Gio-hang.html')

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def map_view(request):
    return render(request, 'map.html')

def tinh_trang_view(request):
    # File của bạn là 'Tinhtrang.html'
    return render(request, 'Tinhtrang.html')