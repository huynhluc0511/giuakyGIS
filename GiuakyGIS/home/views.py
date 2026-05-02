from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dashboard.models import About, CustomerProfile, Review, ReviewImage
from dashboard.forms import CustomerProfileForm, UserBasicInfoForm, ReviewForm

# --- Trang chủ ---
def home_view(request):
    from dashboard.models import News
    
    # Get featured news for ticker (published, featured)
    featured_news = News.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-published_at', '-created_at')[:5]
    
    # Get recent news for slide
    recent_news = News.objects.filter(
        status='published'
    ).order_by('-published_at', '-created_at')[:6]
    
    context = {
        'featured_news': featured_news,
        'recent_news': recent_news,
    }
    return render(request, 'home.html', context)

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
    """Cart page with user info pre-fill if logged in"""
    context = {}
    
    if request.user.is_authenticated:
        try:
            profile = CustomerProfile.objects.get(user=request.user)
            context['user_profile'] = {
                'full_name': request.user.first_name or request.user.username,
                'phone': profile.phone or '',
                'address': profile.address or '',
            }
        except CustomerProfile.DoesNotExist:
            context['user_profile'] = {
                'full_name': request.user.first_name or request.user.username,
                'phone': '',
                'address': '',
            }
    
    return render(request, 'Gio-hang.html', context)

def lien_he_view(request):
    return render(request, 'lien_he.html')

def tinh_trang_view(request):
    """Order status tracking page - can accept order_id or use localStorage"""
    from dashboard.models import Order
    
    order = None
    order_items = []
    
    # Check if order_id is passed in URL
    order_id = request.GET.get('order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order_items = order.items.select_related('product').all()
        except Order.DoesNotExist:
            pass
    
    context = {
        'order': order,
        'order_items': order_items,
        'has_order': order is not None,
    }
    return render(request, 'Tinhtrang.html', context)

def tim_duong(request):
    return render(request, 'tim_duong.html')

def gioi_thieu_view(request):
    """Public About page - displays published About articles"""
    articles = About.objects.filter(
        status='published', 
        is_active=True
    ).order_by('order', '-created_at')
    
    context = {
        'articles': articles,
        'page_title': 'Giới Thiệu - FastFood Universe',
    }
    return render(request, 'gioi-thieu.html', context)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_403(request, exception=None):
    # Ensure session is preserved during 403 error handling
    if hasattr(request, 'session'):
        # Save the session to ensure it's not lost
        request.session.save()
        # Mark session as modified to ensure it's saved
        request.session.modified = True
    
    context = {
        'user_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None,
    }
    return render(request, '403.html', context, status=403)

# --- Xử lý Đăng ký ---
def register_view(request):
    if request.method == 'POST':
        hoten = request.POST.get('hoten')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
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

        # 4. Tạo CustomerProfile với thông tin mặc định
        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            address=address
        )

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
    messages.success(request, '✅ Đăng xuất thành công!')
    return redirect('home')


# --- Customer Profile Views ---
@login_required
def customer_profile_view(request):
    """Customer profile view"""
    try:
        profile = request.user.profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
        'page_title': 'Thông Tin Cá Nhân',
    }
    return render(request, 'customer/profile.html', context)


@login_required
def customer_profile_view_enhanced(request):
    """Enhanced customer profile view with modern design"""
    try:
        profile = request.user.profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
        'page_title': 'Thông Tin Cá Nhân',
    }
    return render(request, 'customer/profile_enhanced.html', context)


@login_required
def customer_profile_edit(request):
    """Customer profile edit view"""
    try:
        profile = request.user.profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserBasicInfoForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, '✅ Thông tin của bạn đã được cập nhật thành công!')
            return redirect('customer_profile')
        else:
            messages.error(request, '❌ Vui lòng sửa các lỗi bên dưới.')
    else:
        profile_form = CustomerProfileForm(instance=profile)
        user_form = UserBasicInfoForm(instance=request.user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
        'page_title': 'Chỉnh Sửa Thông Tin Cá Nhân',
    }
    return render(request, 'customer/profile_edit_enhanced.html', context)


# --- Tin tức (News) ---
def news_list_view(request):
    """Public news list page"""
    from dashboard.models import News
    
    # Get published news
    news_items = News.objects.filter(status='published').order_by('-published_at', '-created_at')
    
    # Get featured news
    featured_news = news_items.filter(is_featured=True)[:3]
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        news_items = news_items.filter(category=category)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        news_items = news_items.filter(title__icontains=search_query)
    
    context = {
        'news_items': news_items,
        'featured_news': featured_news,
        'page_title': 'Tin Tức - FastFood Universe',
        'category_choices': News.CATEGORY_CHOICES,
        'current_category': category,
        'search_query': search_query,
    }
    # Use new store_news.html template
    return render(request, 'news/store_news.html', context)


def news_detail_view(request, slug):
    """Public news detail page"""
    from dashboard.models import News
    
    news = get_object_or_404(News, slug=slug, status='published')
    
    # Increment view count
    news.increment_views()
    
    # Get related news (same category, excluding current)
    related_news = News.objects.filter(
        status='published',
        category=news.category
    ).exclude(pk=news.pk).order_by('-published_at')[:4]
    
    context = {
        'news': news,
        'related_news': related_news,
        'page_title': f'{news.title} - FastFood Universe',
    }
    # Use new store_news_detail.html template
    return render(request, 'news/store_news_detail.html', context)


# --- API for Stores ---
def api_stores_list(request):
    """Public API to get all stores with their coordinates"""
    from dashboard.models import Store
    
    stores = Store.objects.all()
    data = [{
        'id': store.id,
        'name': store.name,
        'address': store.address,
        'latitude': store.latitude,
        'longitude': store.longitude,
        'opening_hours': store.opening_hours,
    } for store in stores]
    
    return JsonResponse(data, safe=False)


def api_nearby_stores(request):
    """Find nearby stores within radius"""
    from dashboard.models import Store
    from dashboard.utils import search_stores_by_location
    
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        radius = float(request.GET.get('radius', 5))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)
    
    nearby = search_stores_by_location(lat, lng, radius)
    nearby = []
    for store in Store.objects.all():
        distance = haversine(lat, lng, store.latitude, store.longitude)
        if distance <= radius:
            nearby.append({
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'latitude': store.latitude,
                'longitude': store.longitude,
                'opening_hours': store.opening_hours,
                'distance': round(distance, 2),
            })
    
    nearby.sort(key=lambda x: x['distance'])
    return JsonResponse(nearby, safe=False)


# --- Customer Reviews ---
@login_required
def submit_review(request, order_item_id):
    """Submit a review for a specific order item (food item in an order)"""
    from dashboard.models import OrderItem, Review
    from dashboard.forms import ReviewForm, ReviewImageForm
    
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = order_item.order
    
    # Check if this order belongs to the current user
    if order.user != request.user:
        messages.error(request, 'Bạn không có quyền đánh giá đơn hàng này!')
        return redirect('customer_profile')
    
    # Check if order is delivered (can only review delivered orders)
    if order.status != 'Delivered':
        messages.error(request, 'Chỉ có thể đánh giá đơn hàng đã giao!')
        return redirect('customer_profile')
    
    # Check if user already reviewed this order_item
    existing_review = Review.objects.filter(order_item=order_item, user=request.user).first()
    if existing_review:
        messages.warning(request, 'Bạn đã đánh giá món này rồi!')
        return redirect('customer_profile')
    
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.order_item = order_item
            review.user = request.user
            review.save()
            
            # Handle multiple images
            images = request.FILES.getlist('images')
            for image in images[:5]:  # Max 5 images
                ReviewImage.objects.create(review=review, image=image)
            
            messages.success(request, 'Cảm ơn bạn đã đánh giá! Đánh giá của bạn đang chờ duyệt.')
            return redirect('customer_profile')
    else:
        review_form = ReviewForm()
    
    context = {
        'order_item': order_item,
        'review_form': review_form,
        'product': order_item.product,
        'page_title': f'Đánh giá {order_item.product.name}',
    }
    return render(request, 'customer/submit_review.html', context)


@login_required
def edit_review(request, review_id):
    """Edit an existing review"""
    from dashboard.models import Review
    from dashboard.forms import ReviewForm
    
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    # Can only edit if still pending
    if review.status != 'pending':
        messages.error(request, 'Không thể chỉnh sửa đánh giá đã được duyệt!')
        return redirect('customer_profile')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật đánh giá!')
            return redirect('customer_profile')
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'page_title': 'Chỉnh sửa đánh giá',
    }
    return render(request, 'customer/edit_review.html', context)


@login_required
def delete_review(request, review_id):
    """Delete a review"""
    from dashboard.models import Review
    
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Đã xóa đánh giá!')
    
    return redirect('customer_profile')


def product_reviews(request, product_id):
    """Display all approved reviews for a product"""
    from dashboard.models import Product, Review
    
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(
        order_item__product=product,
        status='approved'
    ).select_related('user', 'order_item').prefetch_related('images')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': reviews.count(),
        'page_title': f'Đánh giá {product.name}',
    }
    return render(request, 'product_reviews.html', context)


@csrf_exempt
def api_create_order(request):
    """Create order from cart data - called from Gio-hang.html"""
    from dashboard.models import Order, OrderItem, Product
    import json
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Prepare order data
        order_data = {
            'full_name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'total_price': data.get('total', 0),
            'status': 'Pending',
            'lat': data.get('lat'),
            'lng': data.get('lng')
        }
        
        # If user is logged in, associate order with user
        if request.user.is_authenticated:
            order_data['user'] = request.user
            
            # Update user profile with latest info (optional)
            try:
                profile = CustomerProfile.objects.get(user=request.user)
                profile.phone = data.get('phone', profile.phone)
                profile.address = data.get('address', profile.address)
                profile.save()
            except CustomerProfile.DoesNotExist:
                # Create profile if not exists
                CustomerProfile.objects.create(
                    user=request.user,
                    phone=data.get('phone', ''),
                    address=data.get('address', '')
                )
        
        # Create order
        order = Order.objects.create(**order_data)
        
        # Create order items (find product by name since cart uses name as ID)
        for item in data.get('items', []):
            try:
                # Try to find product by name (cart stores name in id field)
                product_name = item.get('name', '').split(' (')[0].split(' x')[0].strip()
                # Try exact match first
                product = Product.objects.filter(name=product_name).first()
                if not product:
                    # Try case-insensitive partial match
                    product = Product.objects.filter(name__icontains=product_name[:20]).first()
                
                if product:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.get('qty', 1),
                        price=item.get('price', 0)
                    )
            except Exception:
                pass
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'redirect_url': f"/tinh-trang/?order_id={order.id}"
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
