from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout

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
    return render(request, 'Gio-hang.html')

def lien_he_view(request):
    return render(request, 'lien_he.html')

def tinh_trang_view(request):
    return render(request, 'Tinhtrang.html')

def tim_duong(request):
    return render(request, 'tim_duong.html')

def custom_404(request, exception):
    return render(request, '404.html', status=404)

# --- Xử lý Đăng ký ---
def register_view(request):
    if request.method == 'POST':
        hoten = request.POST.get('hoten')
        email = request.POST.get('email')
        matkhau = request.POST.get('matkhau')
        xacnhan_matkhau = request.POST.get('xacnhan_matkhau')

        # 1. Kiểm tra mật khẩu khớp
        if matkhau != xacnhan_matkhau:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return redirect('register')

        # 2. Kiểm tra trùng lặp (Dùng Email làm Username để tránh lỗi xác thực)
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email này đã được sử dụng để đăng ký!')
            return redirect('register')

        # 3. Tạo tài khoản (Gán email vào cả username và email)
        user = User.objects.create_user(username=email, email=email, password=matkhau)
        user.first_name = hoten # Lưu họ tên vào trường first_name
        user.save()

        django_login(request, user)
        messages.success(request, f'Đăng ký thành công! Chào mừng {hoten}.')
        return redirect('home')

    return render(request, 'register.html')

# --- Xử lý Đăng nhập ---
def login_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        matkhau_input = request.POST.get('matkhau')
        
        # 1. Tìm user theo email trong database
        try:
            # Django mặc định authenticate qua trường username. 
            # Ta tìm user có email đó để lấy username thực sự của họ.
            user_found = User.objects.get(email=email_input)
            actual_username = user_found.username
        except User.DoesNotExist:
            messages.error(request, '❌ Email không tồn tại trong hệ thống!')
            return redirect('login')
        
        # 2. Xác thực bằng username và mật khẩu
        user = authenticate(request, username=actual_username, password=matkhau_input)
        
        if user is not None:
            django_login(request, user)
            messages.success(request, f'✅ Chào mừng trở lại!')
            
            # Phân quyền chuyển hướng
            if user.is_staff or user.is_superuser:
                # Hãy đảm bảo bạn đã định nghĩa namespace 'dashboard' trong urls.py
                try:
                    return redirect('dashboard:index')
                except:
                    return redirect('home')
            return redirect('home')
        else:
            messages.error(request, '❌ Mật khẩu không chính xác!')
            return redirect('login')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, '✅ Đã đăng xuất thành công!')
    return redirect('home')