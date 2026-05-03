from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from dashboard.models import About, CustomerProfile, Review, Order, OrderItem
from .models import OrderReview, ReviewImage, ReviewReply, ReviewHelpful
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
    """Display drinks products from database"""
    from django.db.models import Q
    from dashboard.models import Product, Category
    
    # Get drinks category
    drinks_category = Category.objects.filter(name__icontains='drinks').first()
    
    # Get all drinks products or filter by name if no drinks category
    if drinks_category:
        products = Product.objects.filter(category=drinks_category, is_available=True)
    else:
        products = Product.objects.filter(
            Q(name__icontains='cola') | Q(name__icontains='pepsi') | Q(name__icontains='juice') | Q(name__icontains='water') | Q(name__icontains='nước'),
            is_available=True
        )
    
    context = {
        'products': products,
        'category_name': 'Đồ Uống',
        'page_title': 'Thực Đơn Đồ Uống - FastFood Universe'
    }
    return render(request, 'do-uong.html', context)

def ga_chien_view(request):
    """Display chicken products from database"""
    from django.db.models import Q
    from dashboard.models import Product, Category
    
    # Get chicken category
    chicken_category = Category.objects.filter(name__icontains='chicken').first()
    
    # Get all chicken products or all products if no chicken category
    if chicken_category:
        products = Product.objects.filter(category=chicken_category, is_available=True)
    else:
        products = Product.objects.filter(Q(name__icontains='chicken') | Q(name__icontains='gà'), is_available=True)
    
    context = {
        'products': products,
        'category_name': 'Gà Chiên',
        'page_title': 'Thực Đơn Gà Chiên - FastFood Universe'
    }
    return render(request, 'ga-chien.html', context)

def hamburger_view(request):
    return render(request, 'hamburger.html')

def khoai_tay_view(request):
    """Display sides products from database"""
    from django.db.models import Q
    from dashboard.models import Product, Category
    
    # Get sides category
    sides_category = Category.objects.filter(name__icontains='sides').first()
    
    # Get all sides products or filter by name if no sides category
    if sides_category:
        products = Product.objects.filter(category=sides_category, is_available=True)
    else:
        products = Product.objects.filter(
            Q(name__icontains='khoai') | Q(name__icontains='fries') | Q(name__icontains='salad') | Q(name__icontains='onion'),
            is_available=True
        )
    
    context = {
        'products': products,
        'category_name': 'Khoai Tây',
        'page_title': 'Thực Đọn Khoai Tây - FastFood Universe'
    }
    return render(request, 'khoai-tay.html', context)

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
    from dashboard.models import Order, DeliveryStatus
    
    order = None
    order_items = []
    delivery = None
    
    # Check if order_id is passed in URL
    order_id = request.GET.get('order_id')
    
    if order_id:
        try:
            order = Order.objects.select_related('shipper__user', 'user').get(id=order_id)
            order_items = order.items.select_related('product').all()
            
            # Get delivery status
            try:
                delivery = DeliveryStatus.objects.select_related('shipper__user').get(order=order)
            except DeliveryStatus.DoesNotExist:
                delivery = None
                
        except Order.DoesNotExist:
            pass
    
    context = {
        'order': order,
        'order_items': order_items,
        'delivery': delivery,
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


# ==================== CUSTOMER REVIEWS ====================
@login_required
def my_orders(request):
    """View customer's orders with review options"""
    orders = Order.objects.filter(user=request.user).prefetch_related(
        'items__product__category', 'items__product'
    ).order_by('-created_at')
    
    # Check review status for each order
    for order in orders:
        order.can_review_order = False
        for item in order.items.all():
            item.can_review_item = False
        
        if order.status == 'Delivered':
            # Check if already reviewed
            has_order_review = OrderReview.objects.filter(order=order, user=request.user).exists()
            order.can_review_order = not has_order_review
            
            # Check which items can be reviewed
            for item in order.items.all():
                has_item_review = Review.objects.filter(order_item=item, user=request.user).exists()
                item.can_review_item = not has_item_review
    
    context = {
        'orders': orders,
        'page_title': 'Đơn hàng của tôi',
    }
    return render(request, 'home/my_orders.html', context)


@login_required
def create_order_review(request, order_id):
    """Create or edit order review"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is delivered
    if order.status != 'Delivered':
        messages.error(request, 'Chỉ có thể đánh giá đơn hàng đã được giao!')
        return redirect('home:my_orders')
    
    # Get or create order review
    order_review, created = OrderReview.objects.get_or_create(
        order=order, 
        user=request.user,
        defaults={
            'overall_rating': 5,
            'food_quality': 5,
            'service_quality': 5,
            'delivery_speed': 5,
            'packaging_quality': 5,
            'content': '',
            'status': 'pending'
        }
    )
    
    if request.method == 'POST':
        # Update order review
        order_review.overall_rating = int(request.POST.get('overall_rating', 5))
        order_review.food_quality = int(request.POST.get('food_quality', 5))
        order_review.service_quality = int(request.POST.get('service_quality', 5))
        order_review.delivery_speed = int(request.POST.get('delivery_speed', 5))
        order_review.packaging_quality = int(request.POST.get('packaging_quality', 5))
        order_review.content = request.POST.get('content', '')
        order_review.status = 'pending'
        order_review.save()
        
        messages.success(request, 'Cảm ơn bạn đã đánh giá đơn hàng! Đánh giá đang chờ duyệt.')
        return redirect('home:my_orders')
    
    context = {
        'order': order,
        'order_review': order_review,
        'is_edit': not created,
        'page_title': f'Đánh giá đơn hàng #{order.id}',
    }
    return render(request, 'home/create_order_review.html', context)


@login_required
def create_product_review(request, order_item_id):
    """Create or edit product review"""
    order_item = get_object_or_404(
        OrderItem.objects.select_related('order', 'product'), 
        id=order_item_id
    )
    
    # Check if order belongs to user and is delivered
    if order_item.order.user != request.user or order_item.order.status != 'Delivered':
        messages.error(request, 'Bạn không có quyền đánh giá sản phẩm này!')
        return redirect('home:my_orders')
    
    # Get or create product review
    review, created = Review.objects.get_or_create(
        order_item=order_item,
        user=request.user,
        defaults={
            'rating': 5,
            'content': '',
            'status': 'pending'
        }
    )
    
    if request.method == 'POST':
        # Update review
        review.rating = int(request.POST.get('rating', 5))
        review.content = request.POST.get('content', '')
        review.status = 'pending'
        review.save()
        
        # Handle review images
        if request.FILES.getlist('images'):
            # Delete old images if any
            review.images.all().delete()
            
            # Add new images
            for image_file in request.FILES.getlist('images'):
                ReviewImage.objects.create(review=review, image=image_file)
        
        messages.success(request, f'Cảm ơn bạn đã đánh giá {order_item.product.name}! Đánh giá đang chờ duyệt.')
        return redirect('home:my_orders')
    
    context = {
        'order_item': order_item,
        'review': review,
        'is_edit': not created,
        'page_title': f'Đánh giá {order_item.product.name}',
    }
    return render(request, 'home/create_product_review.html', context)


@login_required
def my_reviews(request):
    """View customer's reviews"""
    # Get order reviews
    order_reviews = OrderReview.objects.filter(user=request.user).order_by('-created_at')
    
    # Get product reviews
    product_reviews = Review.objects.filter(user=request.user).select_related('order_item__product', 'order_item__order').order_by('-created_at')
    
    context = {
        'order_reviews': order_reviews,
        'product_reviews': product_reviews,
        'page_title': 'Đánh giá của tôi',
    }
    return render(request, 'home/my_reviews.html', context)


@login_required
def edit_order_review(request, review_id):
    """Edit existing order review"""
    order_review = get_object_or_404(OrderReview, id=review_id, user=request.user)
    
    if request.method == 'POST':
        # Update order review
        order_review.overall_rating = int(request.POST.get('overall_rating', 5))
        order_review.food_quality = int(request.POST.get('food_quality', 5))
        order_review.service_quality = int(request.POST.get('service_quality', 5))
        order_review.delivery_speed = int(request.POST.get('delivery_speed', 5))
        order_review.packaging_quality = int(request.POST.get('packaging_quality', 5))
        order_review.content = request.POST.get('content', '')
        order_review.status = 'pending'  # Reset to pending when edited
        order_review.save()
        
        messages.success(request, 'Đã cập nhật đánh giá đơn hàng!')
        return redirect('home:my_reviews')
    
    context = {
        'order_review': order_review,
        'page_title': f'Chỉnh sửa đánh giá đơn hàng #{order_review.order.id}',
    }
    return render(request, 'home/edit_order_review.html', context)


@login_required
def edit_product_review(request, review_id):
    """Edit existing product review"""
    review = get_object_or_404(
        Review.objects.select_related('order_item__product'), 
        id=review_id, 
        user=request.user
    )
    
    if request.method == 'POST':
        # Update review
        review.rating = int(request.POST.get('rating', 5))
        review.content = request.POST.get('content', '')
        review.status = 'pending'  # Reset to pending when edited
        review.save()
        
        # Handle review images
        if request.FILES.getlist('images'):
            # Delete old images if any
            review.images.all().delete()
            
            # Add new images
            for image_file in request.FILES.getlist('images'):
                ReviewImage.objects.create(review=review, image=image_file)
        
        messages.success(request, f'Đã cập nhật đánh giá {review.order_item.product.name}!')
        return redirect('home:my_reviews')
    
    context = {
        'review': review,
        'page_title': f'Chỉnh sửa đánh giá {review.order_item.product.name}',
    }
    return render(request, 'home/edit_product_review.html', context)


# ==================== SHIPPER DELIVERY VIEWS ====================
@login_required
def shipper_dashboard(request):
    """Shipper dashboard - show assigned deliveries and available orders"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        messages.error(request, 'Bạn không phải là shipper!')
        return redirect('home:home')
    
    # Get active deliveries
    active_deliveries = shipper.get_active_deliveries().select_related('order', 'order__user')
    
    # Get completed today
    completed_today = shipper.deliveries.filter(
        status='delivered',
        delivered_at__date=timezone.now().date()
    ).select_related('order').order_by('-delivered_at')[:5]
    
    # Get pending deliveries (assigned but not picked up)
    pending_deliveries = shipper.deliveries.filter(
        status='pending'
    ).select_related('order', 'order__user')
    
    # Get available orders for all shippers (not yet assigned)
    available_orders = DeliveryStatus.objects.filter(
        status='pending',
        shipper__isnull=True,
        is_notified=True  # Only show notified orders
    ).select_related('order', 'order__user').order_by('-created_at')
    
    context = {
        'shipper': shipper,
        'active_deliveries': active_deliveries,
        'completed_today': completed_today,
        'pending_deliveries': pending_deliveries,
        'available_orders': available_orders,
        'page_title': 'Bảng điều khiển Shipper',
    }
    return render(request, 'home/shipper/dashboard.html', context)


@login_required
def shipper_workspace(request):
    """Shipper workspace - comprehensive work interface"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        messages.error(request, 'Bạn không phải là shipper!')
        return redirect('home:home')
    
    # Get available orders
    available_orders = DeliveryStatus.objects.filter(
        status='pending',
        shipper__isnull=True,
        is_notified=True
    ).select_related('order', 'order__user').order_by('-created_at')
    
    # Get active deliveries
    active_deliveries = shipper.get_active_deliveries().select_related('order', 'order__user')
    
    # Get completed today
    completed_today = shipper.deliveries.filter(
        status='delivered',
        delivered_at__date=timezone.now().date()
    ).select_related('order').order_by('-delivered_at')
    
    # Calculate earnings today
    total_earnings = sum(delivery.order.total_price * 0.1 for delivery in completed_today)  # 10% commission
    
    # Calculate performance metrics
    avg_delivery_time = None
    if completed_today.exists():
        total_time = sum(
            (delivery.delivered_at - delivery.assigned_at).total_seconds() / 60
            for delivery in completed_today
            if delivery.delivered_at and delivery.assigned_at
        )
        avg_delivery_time = f"{total_time / completed_today.count():.0f} phút"
    
    avg_rating = None
    if completed_today.exists():
        ratings = [
            delivery.shipper_rating 
            for delivery in completed_today 
            if delivery.shipper_rating
        ]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
    
    context = {
        'shipper': shipper,
        'available_orders': available_orders,
        'active_deliveries': active_deliveries,
        'completed_today': completed_today,
        'total_earnings': total_earnings,
        'avg_delivery_time': avg_delivery_time,
        'avg_rating': avg_rating,
        'page_title': 'Nơi làm việc Shipper',
    }
    return render(request, 'home/shipper/workspace.html', context)


@login_required
def shipper_accept_order(request, delivery_id):
    """Shipper accepts an available order"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        messages.error(request, 'Bạn không phải là shipper!')
        return redirect('home:home')
    
    delivery = get_object_or_404(
        DeliveryStatus.objects.select_related('order'), 
        pk=delivery_id,
        shipper__isnull=True,  # Must be unassigned
        status='pending'
    )
    
    if request.method == 'POST':
        try:
            # Assign order to shipper
            delivery.shipper = shipper
            delivery.assigned_at = timezone.now()
            delivery.status = 'pending'  # Still pending until pickup
            delivery.save()
            
            # Update order
            delivery.order.shipper = shipper
            delivery.order.save()
            
            # Update shipper status to busy
            shipper.status = 'busy'
            shipper.save()
            
            messages.success(request, f'Đã nhận đơn hàng #{delivery.order.id}! Vui lòng chuẩn bị đi lấy hàng.')
            return redirect('home:shipper_delivery_detail', delivery_id=delivery_id)
            
        except Exception as e:
            messages.error(request, f'Lỗi khi nhận đơn hàng: {str(e)}')
    
    context = {
        'delivery': delivery,
        'shipper': shipper,
        'page_title': f'Nhận đơn hàng #{delivery.order.id}',
    }
    return render(request, 'home/shipper/accept_order.html', context)


@login_required
def shipper_available_orders(request):
    """View all available orders for shippers"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        messages.error(request, 'Bạn không phải là shipper!')
        return redirect('home:home')
    
    # Get available orders
    available_orders = DeliveryStatus.objects.filter(
        status='pending',
        shipper__isnull=True,
        is_notified=True
    ).select_related('order', 'order__user').order_by('-created_at')
    
    context = {
        'shipper': shipper,
        'available_orders': available_orders,
        'page_title': 'Đơn hàng có sẵn',
    }
    return render(request, 'home/shipper/available_orders.html', context)


@login_required
def shipper_delivery_detail(request, delivery_id):
    """View delivery details for shipper"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        messages.error(request, 'Bạn không phải là shipper!')
        return redirect('home:home')
    
    delivery = get_object_or_404(
        DeliveryStatus.objects.select_related('order', 'order__user', 'order__items__product'), 
        pk=delivery_id,
        shipper=shipper
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'delivering':
            # Auto-mark as picked up and start delivering
            delivery.update_status('picked_up', notes="Bắt đầu giao hàng")
            delivery.update_status('delivering', notes=notes)
            messages.success(request, 'Đã bắt đầu giao hàng!')
            
        elif action == 'delivered':
            # Handle photo and signature upload
            delivery_photo = request.FILES.get('delivery_photo')
            customer_signature = request.FILES.get('customer_signature')
            delivery.update_status('delivered', notes=notes, photo=delivery_photo)
            
            # Handle signature separately
            if customer_signature:
                delivery.customer_signature = customer_signature
                delivery.save()
            
            # Update shipper status to available
            shipper.status = 'available'
            shipper.save()
            
            messages.success(request, 'Đã hoàn thành giao hàng!')
            
        elif action == 'failed':
            delivery.update_status('failed', notes=notes)
            # Update shipper status to available
            shipper.status = 'available'
            shipper.save()
            messages.warning(request, 'Đánh dấu giao hàng thất bại!')
        
        return redirect('home:shipper_delivery_detail', delivery_id=delivery_id)
    
    context = {
        'delivery': delivery,
        'shipper': shipper,
        'page_title': f'Chi tiết giao hàng #{delivery.order.id}',
    }
    return render(request, 'home/shipper/delivery_detail.html', context)


@login_required
def shipper_update_location(request):
    """Update shipper location (API endpoint)"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        return JsonResponse({'error': 'Not a shipper'}, status=403)
    
    if request.method == 'POST':
        try:
            lat = float(request.POST.get('lat'))
            lng = float(request.POST.get('lng'))
            shipper.update_location(lat, lng)
            return JsonResponse({'success': True})
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid coordinates'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def delivery_location_api(request, delivery_id):
    """API endpoint to get shipper location and delivery status"""
    try:
        delivery = get_object_or_404(
            DeliveryStatus.objects.select_related('shipper', 'order'), 
            pk=delivery_id
        )
        
        response_data = {
            'delivery_id': delivery.id,
            'status': delivery.status,
            'shipper_lat': None,
            'shipper_lng': None,
            'shipper_name': None,
            'updated_at': None,
            'order_lat': delivery.order.lat,
            'order_lng': delivery.order.lng,
            'order_address': delivery.order.address
        }
        
        if delivery.shipper:
            response_data.update({
                'shipper_lat': delivery.shipper.current_latitude,
                'shipper_lng': delivery.shipper.current_longitude,
                'shipper_name': delivery.shipper.user.get_full_name() or delivery.shipper.user.username,
                'updated_at': delivery.shipper.last_location_update
            })
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def shipper_toggle_status(request):
    """Toggle shipper work status (available/busy)"""
    try:
        shipper = request.user.shipper_profile
        
        if shipper.status == 'available':
            shipper.status = 'offline'
        else:
            shipper.status = 'available'
        
        shipper.save()
        
        return JsonResponse({
            'success': True,
            'new_status': shipper.status,
            'display_status': shipper.display_status
        })
        
    except Shipper.DoesNotExist:
        return JsonResponse({'error': 'Shipper not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def shipper_stats_api(request):
    """API endpoint for real-time shipper stats"""
    try:
        shipper = request.user.shipper_profile
        
        available_orders = DeliveryStatus.objects.filter(
            status='pending',
            shipper__isnull=True,
            is_notified=True
        ).count()
        
        active_deliveries = shipper.get_active_deliveries().count()
        
        completed_today = shipper.deliveries.filter(
            status='delivered',
            delivered_at__date=timezone.now().date()
        ).count()
        
        return JsonResponse({
            'available_orders': available_orders,
            'active_deliveries': active_deliveries,
            'completed_today': completed_today
        })
        
    except Shipper.DoesNotExist:
        return JsonResponse({'error': 'Shipper not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delivery_details_api(request, delivery_id):
    """API endpoint to get detailed delivery information"""
    try:
        delivery = get_object_or_404(
            DeliveryStatus.objects.select_related('order', 'order__items__product'), 
            pk=delivery_id
        )
        
        items = []
        for item in delivery.order.items.all():
            items.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': item.price
            })
        
        response_data = {
            'order': {
                'id': delivery.order.id,
                'full_name': delivery.order.full_name,
                'phone': delivery.order.phone,
                'address': delivery.order.address,
                'total_price': delivery.order.total_price
            },
            'items': items,
            'delivery': {
                'status': delivery.status,
                'created_at': delivery.created_at.isoformat(),
                'assigned_at': delivery.assigned_at.isoformat() if delivery.assigned_at else None
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def shipper_profile(request):
    """View and edit shipper profile"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        messages.error(request, 'Bạn không phải là shipper!')
        return redirect('home:home')
    
    if request.method == 'POST':
        # Update shipper info
        shipper.phone = request.POST.get('phone', shipper.phone)
        shipper.license_plate = request.POST.get('license_plate', shipper.license_plate)
        shipper.vehicle_type = request.POST.get('vehicle_type', shipper.vehicle_type)
        shipper.save()
        
        # Update user info
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'Đã cập nhật thông tin cá nhân!')
        return redirect('home:shipper_profile')
    
    # Get statistics
    stats = {
        'total_deliveries': shipper.deliveries.count(),
        'completed_deliveries': shipper.deliveries.filter(status='delivered').count(),
        'completed_today': shipper.get_completed_deliveries_today(),
        'active_deliveries': shipper.get_active_deliveries().count(),
    }
    
    context = {
        'shipper': shipper,
        'stats': stats,
        'page_title': 'Hồ sơ Shipper',
    }
    return render(request, 'home/shipper/profile.html', context)


@login_required
def shipper_delivery_history(request):
    """View delivery history for shipper"""
    try:
        shipper = request.user.shipper_profile
    except Shipper.DoesNotExist:
        messages.error(request, 'Bạn không phải là shipper!')
        return redirect('home:home')
    
    # Get all deliveries with pagination
    deliveries = shipper.deliveries.select_related('order', 'order__user').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        deliveries = deliveries.filter(created_at__date__gte=start_date)
    if end_date:
        deliveries = deliveries.filter(created_at__date__lte=end_date)
    
    # Pagination
    from .utils import paginate_queryset
    page_obj, paginator = paginate_queryset(deliveries, request.GET.get('page'), 10)
    
    context = {
        'deliveries': page_obj,
        'paginator': paginator,
        'shipper': shipper,
        'page_title': 'Lịch sử giao hàng',
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'home/shipper/delivery_history.html', context)


# --- ORDER REVIEW VIEWS ---
@login_required
def rate_order(request, order_id):
    """View for rating an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is delivered
    if order.status != 'Delivered':
        messages.error(request, 'Chỉ có thể đánh giá đơn hàng đã được giao thành công!')
        return redirect('home:my_orders')
    
    # Check if already reviewed
    existing_review = None
    try:
        existing_review = order.order_review
    except OrderReview.DoesNotExist:
        pass
    
    if request.method == 'POST':
        return submit_order_review(request, order_id)
    
    context = {
        'order': order,
        'existing_review': existing_review,
        'page_title': f'Đánh giá đơn hàng #{order.id}',
    }
    return render(request, 'home/rate_order.html', context)


@login_required
def submit_order_review(request, order_id):
    """Handle order review submission"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is delivered
    if order.status != 'Delivered':
        return JsonResponse({'error': 'Chỉ có thể đánh giá đơn hàng đã được giao thành công!'}, status=400)
    
    # Check if already reviewed
    try:
        existing_review = order.order_review
        return JsonResponse({'error': 'Bạn đã đánh giá đơn hàng này rồi!'}, status=400)
    except OrderReview.DoesNotExist:
        pass
    
    # Get form data
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '')
    is_recommended = request.POST.get('is_recommended') == 'on'
    
    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return JsonResponse({'error': 'Đánh giá phải từ 1 đến 5 sao!'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Đánh giá không hợp lệ!'}, status=400)
    
    try:
        # Create review
        review = OrderReview.objects.create(
            order=order,
            user=request.user,
            rating=rating,
            comment=comment,
            is_recommended=is_recommended
        )
        
        # Handle image uploads
        images = request.FILES.getlist('images')
        for image in images:
            ReviewImage.objects.create(
                review=review,
                image=image
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Đánh giá đã được gửi thành công!',
            'review': {
                'rating_stars': review.rating_stars,
                'comment': review.comment
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Có lỗi xảy ra: {str(e)}'}, status=500)


@login_required
def edit_order_review(request, review_id):
    """Edit an existing order review"""
    review = get_object_or_404(OrderReview, id=review_id, user=request.user)
    order = review.order
    
    if request.method == 'POST':
        # Get form data
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        is_recommended = request.POST.get('is_recommended') == 'on'
        
        # Validate rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, 'Đánh giá phải từ 1 đến 5 sao!')
                return redirect('home:edit_order_review', review_id=review.id)
        except (ValueError, TypeError):
            messages.error(request, 'Đánh giá không hợp lệ!')
            return redirect('home:edit_order_review', review_id=review.id)
        
        try:
            # Update review
            review.rating = rating
            review.comment = comment
            review.is_recommended = is_recommended
            review.save()
            
            # Handle new image uploads
            images = request.FILES.getlist('images')
            for image in images:
                ReviewImage.objects.create(
                    review=review,
                    image=image
                )
            
            # Handle image deletions
            delete_images = request.POST.getlist('delete_images')
            for image_id in delete_images:
                try:
                    image = ReviewImage.objects.get(id=image_id, review=review)
                    image.image.delete()
                    image.delete()
                except ReviewImage.DoesNotExist:
                    continue
            
            messages.success(request, 'Đánh giá đã được cập nhật thành công!')
            return redirect('home:my_orders')
            
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    context = {
        'order': order,
        'review': review,
        'page_title': f'Chỉnh sửa đánh giá đơn hàng #{order.id}',
    }
    return render(request, 'home/edit_order_review.html', context)


@login_required
def delete_review_image(request, image_id):
    """Delete a review image via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        image = ReviewImage.objects.get(id=image_id)
        review = image.review
        
        # Check if user owns this review
        if review.user != request.user:
            return JsonResponse({'error': 'Không có quyền xóa ảnh này!'}, status=403)
        
        # Delete image file and record
        image.image.delete()
        image.delete()
        
        return JsonResponse({'success': True, 'message': 'Ảnh đã được xóa thành công!'})
        
    except ReviewImage.DoesNotExist:
        return JsonResponse({'error': 'Ảnh không tồn tại!'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Có lỗi xảy ra: {str(e)}'}, status=500)


@login_required
def my_reviews(request):
    """View all reviews by current user"""
    reviews = OrderReview.objects.filter(
        user=request.user
    ).select_related('order').order_by('-created_at')
    
    context = {
        'reviews': reviews,
        'page_title': 'Đánh giá của tôi',
    }
    return render(request, 'home/my_reviews.html', context)


@login_required
def order_delivered_notification(request, order_id):
    """Show notification when order is delivered"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is delivered
    if order.status != 'Delivered':
        messages.error(request, 'Đơn hàng này chưa được giao!')
        return redirect('home:my_orders')
    
    # Check if already reviewed
    try:
        existing_review = order.order_review
        has_reviewed = True
    except OrderReview.DoesNotExist:
        has_reviewed = False
    
    context = {
        'order': order,
        'has_reviewed': has_reviewed,
        'page_title': f'Đơn hàng #{order.id} đã giao!',
    }
    return render(request, 'home/order_delivered_notification.html', context)
