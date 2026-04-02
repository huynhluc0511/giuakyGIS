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
# Thêm các dòng import này lên TRÊN CÙNG của views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login

# ... (các hàm hiện tại của bạn như home_view, tim_duong_view cứ giữ nguyên) ...

# Thêm hàm này vào CUỐI file views.py
def register_view(request):
    if request.method == 'POST':
        hoten = request.POST.get('hoten')
        email = request.POST.get('email')
        matkhau = request.POST.get('matkhau')
        xacnhan_matkhau = request.POST.get('xacnhan_matkhau')
        # loai_tk = request.POST.get('loai_tk') # Có thể dùng sau nếu bạn có Model riêng

        # Kiểm tra mật khẩu khớp nhau
        if matkhau != xacnhan_matkhau:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return redirect('register')

        # Kiểm tra xem tên đăng nhập (họ tên) đã tồn tại chưa
        if User.objects.filter(username=hoten).exists():
            messages.error(request, 'Tên người dùng này đã được sử dụng!')
            return redirect('register')

        # Tạo tài khoản và lưu vào database
        user = User.objects.create_user(username=hoten, email=email, password=matkhau)
        user.save()

        # Đăng nhập luôn cho khách hàng sau khi đăng ký thành công
        login(request, user)
        return redirect('home') # Chuyển hướng về trang chủ

    return render(request, 'register.html')

def lien_he_view(request):
    return render(request, 'lien_he.html')

def tinh_trang_view(request):
    # File của bạn là 'Tinhtrang.html'
    return render(request, 'Tinhtrang.html')

def tim_duong(request):
    return render(request, 'tim_duong.html')
def custom_404(request, exception):
    return render(request, '404.html', status=404)