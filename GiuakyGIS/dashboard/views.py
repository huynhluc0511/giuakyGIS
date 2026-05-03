from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse
from django.utils import timezone

from dashboard.models import Store, Product, Order, OrderItem, Category, About, CustomerProfile, News, Review, ReviewImage, OrderReview, Shipper, DeliveryStatus
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer, StoreSerializer, OrderSerializer, CategorySerializer
from .forms import (
    StoreForm, ProductForm, OrderForm, CategoryForm, SearchForm, UserForm, AboutForm, AboutImportForm,
    CustomerProfileForm, UserBasicInfoForm, NewsForm, ReviewReplyForm
)
from .utils import admin_required, search_items, paginate_queryset, get_stats


# ==================== DASHBOARD ====================
@admin_required
def dashboard_index(request):
    stats = get_stats()
    recent_orders = Order.objects.prefetch_related('items').all().order_by('-created_at')[:5]
    recent_products = Product.objects.all().order_by('-id')[:5]
    
    # Get top users by order count
    top_customers = User.objects.annotate(
        order_count=models.Count('order')
    ).filter(order_count__gt=0).order_by('-order_count')[:5]
    
    # Get popular products (most ordered)
    popular_products = Product.objects.annotate(
        order_count=models.Count('orderitem')
    ).order_by('-order_count')[:5]
    
    # Get low stock products
    low_stock_products = Product.objects.filter(
        is_available=True,
        orderitem__isnull=False
    ).annotate(
        sold_count=models.Count('orderitem')
    ).order_by('sold_count')[:5]
    
    # Get recent users
    recent_customers = User.objects.order_by('-date_joined')[:5]
    
    # Get published news
    recent_news = News.objects.filter(status='published').order_by('-published_at')[:5]
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'top_customers': top_customers,
        'popular_products': popular_products,
        'low_stock_products': low_stock_products,
        'recent_customers': recent_customers,
        'recent_news': recent_news,
        'page_title': 'Bảng Điều Khiển',
    }
    return render(request, 'dashboard/index.html', context)


# ==================== STORES ====================
@admin_required
def stores_list(request):
    stores = Store.objects.all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        stores = search_items(stores, q, ['name', 'address'])
    page_obj, paginator = paginate_queryset(stores, request.GET.get('page'), 15)
    return render(request, 'dashboard/stores/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'page_title': 'Quản Lý Cửa Hàng',
    })

@admin_required
def stores_detail(request, pk):
    store = get_object_or_404(Store, pk=pk)
    return render(request, 'dashboard/stores/detail.html', {
        'store': store, 'page_title': f'Chi tiết: {store.name}',
    })

@admin_required
def stores_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cửa hàng đã được tạo thành công!')
            return redirect('dashboard:stores_list')
    else:
        form = StoreForm()
    return render(request, 'dashboard/stores/form.html', {
        'form': form, 'page_title': 'Thêm Cửa Hàng', 'is_create': True,
    })

@admin_required
def stores_edit(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cửa hàng đã được cập nhật!')
            return redirect('dashboard:stores_list')
    else:
        form = StoreForm(instance=store)
    return render(request, 'dashboard/stores/form.html', {
        'form': form, 'store': store, 'page_title': f'Chỉnh sửa: {store.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def stores_delete(request, pk):
    store = get_object_or_404(Store, pk=pk)
    name = store.name
    store.delete()
    messages.success(request, f'Cửa hàng "{name}" đã được xóa!')
    return redirect('dashboard:stores_list')


# ==================== CATEGORIES ====================
@admin_required
def categories_list(request):
    categories = Category.objects.all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        categories = search_items(categories, q, ['name', 'slug'])
    page_obj, paginator = paginate_queryset(categories, request.GET.get('page'), 15)
    return render(request, 'dashboard/categories/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'page_title': 'Quản Lý Danh Mục',
    })

@admin_required
def categories_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được tạo!')
            return redirect('dashboard:categories_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/categories/form.html', {
        'form': form, 'page_title': 'Thêm Danh Mục', 'is_create': True,
    })

@admin_required
def categories_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được cập nhật!')
            return redirect('dashboard:categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/categories/form.html', {
        'form': form, 'category': category,
        'page_title': f'Chỉnh sửa: {category.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def categories_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    category.delete()
    messages.success(request, f'Danh mục "{name}" đã được xóa!')
    return redirect('dashboard:categories_list')


# ==================== PRODUCTS ====================
@admin_required
def products_list(request):
    products = Product.objects.select_related('category').all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        products = search_items(products, q, ['name', 'description', 'category__name'])
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__id=category_filter)
    available_filter = request.GET.get('available')
    if available_filter == '1':
        products = products.filter(is_available=True)
    elif available_filter == '0':
        products = products.filter(is_available=False)
    page_obj, paginator = paginate_queryset(products, request.GET.get('page'), 6)
    categories = Category.objects.all()
    return render(request, 'dashboard/products/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'categories': categories,
        'current_category': category_filter, 'page_title': 'Quản Lý Món Ăn',
    })

@admin_required
def products_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'dashboard/products/detail.html', {
        'product': product, 'page_title': f'Chi tiết: {product.name}',
    })

@admin_required
def products_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Món ăn đã được thêm thành công!')
            return redirect('dashboard:products_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/products/form.html', {
        'form': form, 'page_title': 'Thêm Món Ăn', 'is_create': True,
    })

@admin_required
def products_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Món ăn đã được cập nhật!')
            return redirect('dashboard:products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/products/form.html', {
        'form': form, 'product': product,
        'page_title': f'Chỉnh sửa: {product.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def products_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.success(request, f'Món ăn "{name}" đã được xóa!')
    return redirect('dashboard:products_list')


# ==================== ORDERS ====================
@admin_required
def orders_list(request):
    orders = Order.objects.select_related('user').annotate(
        items_count=models.Count('items')
    ).order_by('-created_at')
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        orders = search_items(orders, q, ['full_name', 'phone', 'address', 'user__username'])
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    page_obj, paginator = paginate_queryset(orders, request.GET.get('page'), 6)
    status_choices = Order.STATUS_CHOICES
    return render(request, 'dashboard/orders/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'status_choices': status_choices,
        'current_status': status_filter, 'page_title': 'Quản Lý Đơn Hàng',
    })

@admin_required
def orders_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đơn hàng đã được tạo thành công!')
            return redirect('dashboard:orders_list')
    else:
        form = OrderForm()
    return render(request, 'dashboard/orders/form.html', {
        'form': form, 'page_title': 'Thêm Đơn Hàng', 'is_create': True,
    })

@admin_required
def orders_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('shipper__user', 'user'), 
        pk=pk
    )
    items = order.items.select_related('product', 'product__category').all()
    
    # Get or create delivery status
    delivery, created = DeliveryStatus.objects.get_or_create(
        order=order,
        defaults={'status': 'pending'}
    )
    
    # Get available shippers for assignment
    available_shippers = Shipper.objects.filter(
        status='available', 
        is_active=True
    ).order_by('user__username')
    
    total_quantity = sum(item.quantity for item in items)
    
    return render(request, 'dashboard/orders/detail.html', {
        'order': order, 
        'items': items, 
        'total_quantity': total_quantity,
        'delivery': delivery,
        'available_shippers': available_shippers,
        'page_title': f'Đơn Hàng #{order.id}',
    })

@admin_required
def orders_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    old_status = order.status  # Lưu trạng thái cũ
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save()
            new_status = updated_order.status
            
            # Kiểm tra nếu trạng thái thay đổi thành "Shipped" (đang giao hàng)
            if old_status != new_status and new_status == 'Shipped':
                # Tự động gửi thông báo cho tất cả shipper
                try:
                    delivery, created = DeliveryStatus.objects.get_or_create(
                        order=updated_order,
                        defaults={'status': 'pending'}
                    )
                    
                    # Đánh dấu là đã thông báo
                    delivery.is_notified = True
                    delivery.notification_sent_at = timezone.now()
                    delivery.shipper = None  # Chưa gán shipper cụ thể
                    delivery.status = 'pending'
                    delivery.save()
                    
                    messages.success(request, f'Đơn hàng #{updated_order.id} đã được cập nhật và thông báo cho tất cả shipper!')
                    
                except Exception as e:
                    messages.warning(request, f'Đơn hàng đã được cập nhật nhưng có lỗi khi gửi thông báo: {str(e)}')
            else:
                messages.success(request, 'Đơn hàng đã được cập nhật!')
            
            return redirect('dashboard:orders_detail', pk=updated_order.pk)
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'dashboard/orders/form.html', {
        'form': form, 'order': order,
        'page_title': f'Chỉnh sửa Đơn #{order.id}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def orders_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    messages.success(request, f'Đơn hàng #{pk} đã được xóa!')
    return redirect('dashboard:orders_list')


@admin_required
def orders_assign_shipper(request, pk):
    """Assign shipper to order"""
    order = get_object_or_404(
        Order.objects.select_related('shipper__user', 'user'), 
        pk=pk
    )
    
    # Get or create delivery status
    delivery, created = DeliveryStatus.objects.get_or_create(
        order=order,
        defaults={'status': 'pending'}
    )
    
    if request.method == 'POST':
        shipper_id = request.POST.get('shipper')
        if shipper_id:
            shipper = get_object_or_404(Shipper, pk=shipper_id)
            
            # Update delivery
            delivery.shipper = shipper
            delivery.assigned_at = timezone.now()
            delivery.status = 'pending'
            delivery.save()
            
            # Update order
            order.shipper = shipper
            order.save()
            
            # Update shipper status to busy
            shipper.status = 'busy'
            shipper.save()
            
            messages.success(request, f'Đã gán shipper {shipper.user.get_full_name() or shipper.user.username} cho đơn hàng #{order.id}!')
        else:
            messages.error(request, 'Vui lòng chọn shipper!')
        
        return redirect('dashboard:orders_detail', pk=pk)
    
    # Get available shippers
    available_shippers = Shipper.objects.filter(
        status='available', 
        is_active=True
    ).order_by('user__username')
    
    context = {
        'order': order,
        'delivery': delivery,
        'available_shippers': available_shippers,
        'page_title': f'Gán Shipper cho đơn hàng #{order.id}',
    }
    return render(request, 'dashboard/orders/assign_shipper.html', context)


@admin_required
def orders_notify_shippers(request, pk):
    """Notify all shippers about available order"""
    order = get_object_or_404(
        Order.objects.select_related('user'), 
        pk=pk
    )
    
    # Get or create delivery status
    delivery, created = DeliveryStatus.objects.get_or_create(
        order=order,
        defaults={'status': 'pending'}
    )
    
    if request.method == 'POST':
        # Mark as notified
        delivery.is_notified = True
        delivery.notification_sent_at = timezone.now()
        delivery.shipper = None  # Ensure no shipper is assigned yet
        delivery.status = 'pending'
        delivery.save()
        
        # Update order status to indicate ready for pickup
        if order.status == 'Processing':
            order.status = 'Shipped'
            order.save()
        
        messages.success(request, f'Đã gửi thông báo đơn hàng #{order.id} cho tất cả shipper!')
        return redirect('dashboard:orders_detail', pk=pk)
    
    context = {
        'order': order,
        'delivery': delivery,
        'page_title': f'Gửi thông báo đơn hàng #{order.id}',
    }
    return render(request, 'dashboard/orders/notify_shippers.html', context)


# ==================== USERS ====================
@admin_required
def users_list(request):
    users = User.objects.all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        users = search_items(users, q, ['username', 'email', 'first_name', 'last_name'])
    page_obj, paginator = paginate_queryset(users, request.GET.get('page'), 6)
    return render(request, 'dashboard/users/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'page_title': 'Quản Lý Người Dùng',
    })

@admin_required
def users_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'Người dùng "{user.username}" đã được tạo thành công!')
            return redirect('dashboard:users_detail', pk=user.pk)
    else:
        form = UserForm()
    return render(request, 'dashboard/users/form.html', {
        'form': form, 'is_create': True,
        'page_title': 'Thêm Người Dùng',
    })

@admin_required
def users_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    return render(request, 'dashboard/users/detail.html', {
        'user_obj': user, 'orders': orders,
        'page_title': f'Chi tiết: {user.get_full_name() or user.username}',
    })

@admin_required
def users_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            u = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                u.set_password(password)
            u.save()
            messages.success(request, 'Người dùng đã được cập nhật!')
            return redirect('dashboard:users_detail', pk=user.pk)
    else:
        form = UserForm(instance=user)
    return render(request, 'dashboard/users/form.html', {
        'form': form, 'user_obj': user, 'is_create': False,
        'page_title': f'Chỉnh sửa: {user.get_full_name() or user.username}',
    })

@admin_required
@require_http_methods(["POST"])
def users_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    username = user.get_full_name() or user.username
    user.delete()
    messages.success(request, f'Người dùng "{username}" đã được xóa!')
    return redirect('dashboard:users_list')


# ==================== WAREHOUSE ====================
@admin_required
def warehouse_list(request):
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    try:
        from dashboard.models import Warehouse, WarehouseItem, WarehouseTransaction, WarehouseBatch
        from django.core.paginator import Paginator
        from django.db import models
        
        # Lấy tất cả batches và transactions, gộp lại theo thời gian
        combined_list = []
        
        # Thêm transactions (cũ)
        all_transactions = WarehouseTransaction.objects.select_related(
            'warehouse_item__product', 'warehouse_item__warehouse__store'
        ).order_by('-created_at')
        
        for trans in all_transactions:
            combined_list.append({
                'id': trans.id,
                'type': 'transaction',
                'date': trans.created_at,
                'product': trans.warehouse_item.product.name,
                'quantity': trans.quantity,
                'unit_price': trans.unit_price,
                'batch_type': 'Xuất kho' if trans.transaction_type == 'export' else 'Nhập kho',
                'supplier': trans.supplier or 'N/A',
                'store': trans.warehouse_item.warehouse.store.name,
                'note': trans.note or '',
                'obj': trans
            })
        
        # Thêm batches (mới)
        all_batches = WarehouseBatch.objects.select_related(
            'warehouse__store', 'created_by'
        ).order_by('-created_at')
        
        for batch in all_batches:
            try:
                items_count = batch.items.count()
                total_qty = sum([item.quantity for item in batch.items.all()])
            except:
                items_count = 0
                total_qty = 0
                
            combined_list.append({
                'id': batch.id,
                'type': 'batch',
                'date': batch.created_at,
                'product': f'{items_count} sản phẩm',
                'quantity': total_qty,
                'unit_price': 0,
                'batch_type': 'Xuất kho' if batch.batch_type == 'export' else 'Nhập kho',
                'supplier': batch.supplier or 'N/A',
                'store': batch.warehouse.store.name,
                'note': batch.description or '',
                'obj': batch
            })
        
        # Sắp xếp theo thời gian
        combined_list.sort(key=lambda x: x['date'], reverse=True)
        
        # Phân trang bằng Paginator
        trans_page = request.GET.get('trans_page', 1)
        paginator = Paginator(combined_list, 6)
        try:
            transaction_page_obj = paginator.page(trans_page)
        except:
            transaction_page_obj = paginator.page(1)
        
        # Lấy sản phẩm với tồn kho thấp
        low_stock_items = WarehouseItem.objects.filter(
            quantity__lte=models.F('min_quantity')
        ).select_related('product', 'warehouse__store')
        
        # Lấy tất cả sản phẩm trong kho (có phân trang)
        warehouse_items = WarehouseItem.objects.select_related('product', 'warehouse__store').all()
        page_num = request.GET.get('page', 1)
        paginator_items = Paginator(warehouse_items, 6)
        try:
            page_obj = paginator_items.page(page_num)
        except:
            page_obj = paginator_items.page(1)
        
        return render(request, 'dashboard/warehouse/list.html', {
            'transaction_page_obj': transaction_page_obj,
            'transaction_paginator': paginator,
            'low_stock_items': low_stock_items,
            'page_obj': page_obj,
            'paginator': paginator_items,
            'page_title': 'Quản Lý Kho',
        })
    except Exception as e:
        logger.error(f'Error in warehouse_list: {str(e)}')
        logger.error(traceback.format_exc())
        raise

@admin_required
def warehouse_detail(request, pk):
    from dashboard.models import Warehouse
    warehouse = get_object_or_404(Warehouse, pk=pk)
    return render(request, 'dashboard/warehouse/detail.html', {
        'warehouse': warehouse, 'page_title': f'Kho - {warehouse.store.name}',
    })

@admin_required
def warehouse_create(request):
    from dashboard.models import Warehouse
    from dashboard.forms import WarehouseForm
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quản lý kho đã được thêm!')
            return redirect('dashboard:warehouse_list')
    else:
        form = WarehouseForm()
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'page_title': 'Thêm Quản Lý Kho', 'is_create': True,
    })

@admin_required
def warehouse_edit(request, pk):
    from dashboard.models import Warehouse
    from dashboard.forms import WarehouseForm
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quản lý kho đã được cập nhật!')
            return redirect('dashboard:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'warehouse': warehouse,
        'page_title': f'Chỉnh Sửa Kho - {warehouse.store.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def warehouse_delete(request, pk):
    from dashboard.models import Warehouse
    warehouse = get_object_or_404(Warehouse, pk=pk)
    warehouse.delete()
    messages.success(request, 'Quản lý kho đã được xóa!')
    return redirect('dashboard:warehouse_list')


# ==================== WAREHOUSE ITEM ====================
@admin_required
def warehouse_item_create(request):
    from dashboard.models import WarehouseItem
    from dashboard.forms import WarehouseItemForm
    if request.method == 'POST':
        form = WarehouseItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được thêm vào kho!')
            return redirect('dashboard:warehouse_list')
    else:
        form = WarehouseItemForm()
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'page_title': 'Thêm Sản Phẩm Vào Kho', 'is_item': True, 'is_create': True,
    })

@admin_required
def warehouse_item_edit(request, pk):
    from dashboard.models import WarehouseItem
    from dashboard.forms import WarehouseItemForm
    item = get_object_or_404(WarehouseItem, pk=pk)
    if request.method == 'POST':
        form = WarehouseItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được cập nhật!')
            return redirect('dashboard:warehouse_list')
    else:
        form = WarehouseItemForm(instance=item)
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'page_title': 'Chỉnh Sửa Sản Phẩm', 'is_item': True, 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def warehouse_item_delete(request, pk):
    from dashboard.models import WarehouseItem
    item = get_object_or_404(WarehouseItem, pk=pk)
    item.delete()
    messages.success(request, 'Sản phẩm đã được xóa khỏi kho!')
    return redirect('dashboard:warehouse_list')


# ==================== WAREHOUSE TRANSACTION ====================
@admin_required
def warehouse_transaction_create(request):
    """Chuyển hướng sang batch create (cho phép nhập nhiều sản phẩm cùng lúc)"""
    return redirect('dashboard:warehouse_batch_create')

@admin_required
@require_http_methods(["POST"])
def warehouse_transaction_delete(request, pk):
    from dashboard.models import WarehouseTransaction
    transaction = get_object_or_404(WarehouseTransaction, pk=pk)
    item = transaction.warehouse_item
    
    # Hoàn tác số lượng
    if transaction.transaction_type == 'import':
        item.quantity -= transaction.quantity
    else:
        item.quantity += transaction.quantity
    item.save()
    
    transaction.delete()
    messages.success(request, 'Giao dịch đã được xóa!')
    return redirect('dashboard:warehouse_list')


# ==================== MANAGE STORES LEGACY ====================
@admin_required
def manage_stores_view(request):
    return render(request, 'dashboard/manage_stores.html')


# ==================== WAREHOUSE BATCH (NEW) ====================
@admin_required
def warehouse_batch_list(request):
    from dashboard.models import WarehouseBatch
    batches = WarehouseBatch.objects.select_related('warehouse__store', 'created_by').order_by('-created_at')
    batch_type_filter = request.GET.get('batch_type')
    if batch_type_filter:
        batches = batches.filter(batch_type=batch_type_filter)
    page_obj, paginator = paginate_queryset(batches, request.GET.get('page'), 10)
    return render(request, 'dashboard/warehouse/batch_list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'page_title': 'Phiếu Nhập/Xuất Kho',
    })

@admin_required
def warehouse_batch_create(request):
    from dashboard.models import WarehouseBatch, WarehouseItem, WarehouseBatchItem
    from dashboard.forms import WarehouseBatchForm
    from dashboard.utils import generate_batch_number
    from django.utils import timezone
    import openpyxl
    import csv
    
    if request.method == 'POST':
        action = request.POST.get('action', 'create')
        form = WarehouseBatchForm(request.POST)
        
        if action == 'import-excel':
            # ===== XỬ LÝ IMPORT EXCEL =====
            if 'excel_file' not in request.FILES:
                messages.error(request, '❌ Vui lòng chọn file Excel!')
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
            
            # Tạo batch trước
            if not form.is_valid():
                messages.error(request, f'❌ Lỗi form: {form.errors}')
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
            
            batch = form.save(commit=False)
            batch.created_by = request.user
            if not batch.batch_number:
                batch.batch_number = generate_batch_number(batch.batch_type)
            batch.save()
            
            # Xử lý file Excel
            try:
                excel_file = request.FILES['excel_file']
                filename = excel_file.name.lower()
                
                # ===== XÓA ITEM CŨ (LƯU THAY THẾ) =====
                batch.items.all().delete()
                
                rows_added = 0
                errors = []
                
                if filename.endswith('.csv'):
                    # ===== XỬ LÝ CSV =====
                    import io
                    file_content = io.TextIOWrapper(excel_file.file, encoding='utf-8')
                    reader = csv.reader(file_content)
                    next(reader)  # Bỏ header
                    
                    for row_num, row in enumerate(reader, start=2):
                        if not row or not row[0].strip():
                            continue
                        try:
                            product_name = row[0].strip()
                            quantity = int(row[1]) if len(row) > 1 else 1
                            unit_price = float(row[2]) if len(row) > 2 else 0
                            
                            # Tìm sản phẩm trong kho
                            warehouse_item = WarehouseItem.objects.filter(
                                warehouse=batch.warehouse,
                                product__name__icontains=product_name
                            ).first()
                            
                            if not warehouse_item:
                                errors.append(f"❌ Hàng {row_num}: Sản phẩm '{product_name}' không tìm thấy")
                                continue
                            
                            # Tạo batch item
                            WarehouseBatchItem.objects.create(
                                batch=batch,
                                warehouse_item=warehouse_item,
                                quantity=quantity,
                                unit_price=unit_price
                            )
                            rows_added += 1
                        except (ValueError, IndexError) as e:
                            errors.append(f"❌ Hàng {row_num}: Lỗi dữ liệu - {str(e)}")
                            continue
                
                elif filename.endswith(('.xlsx', '.xls')):
                    # ===== XỬ LÝ EXCEL =====
                    try:
                        wb = openpyxl.load_workbook(excel_file)
                        ws = wb.active
                        
                        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                            if not row or not row[0]:
                                continue
                            try:
                                product_name = str(row[0]).strip()
                                quantity = int(row[1]) if row[1] else 1
                                unit_price = float(row[2]) if row[2] else 0
                                
                                # Tìm sản phẩm trong kho
                                warehouse_item = WarehouseItem.objects.filter(
                                    warehouse=batch.warehouse,
                                    product__name__icontains=product_name
                                ).first()
                                
                                if not warehouse_item:
                                    errors.append(f"❌ Hàng {row_num}: Sản phẩm '{product_name}' không tìm thấy")
                                    continue
                                
                                # Tạo batch item
                                WarehouseBatchItem.objects.create(
                                    batch=batch,
                                    warehouse_item=warehouse_item,
                                    quantity=quantity,
                                    unit_price=unit_price
                                )
                                rows_added += 1
                            except (ValueError, TypeError) as e:
                                errors.append(f"❌ Hàng {row_num}: {str(e)}")
                                continue
                    except Exception as e:
                        messages.error(request, f'❌ Lỗi đọc file Excel: {str(e)}')
                        batch.delete()
                        return render(request, 'dashboard/warehouse/batch_form.html', {
                            'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                        })
                else:
                    messages.error(request, '❌ Định dạng file không hỗ trợ. Vui lòng upload .xlsx, .xls hoặc .csv')
                    batch.delete()
                    return render(request, 'dashboard/warehouse/batch_form.html', {
                        'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                    })
                
                # ===== CẬP NHẬT NGÀY TẠO LẠI =====
                batch.created_at = timezone.now()
                batch.calculate_total()
                batch.save()
                
                # Hiển thị kết quả
                msg = f'✅ Import thành công {rows_added} sản phẩm'
                if errors:
                    msg += f' ({len(errors)} lỗi)'
                    for error in errors[:5]:  # Hiển thị 5 lỗi đầu
                        messages.warning(request, error)
                    if len(errors) > 5:
                        messages.warning(request, f'... và {len(errors)-5} lỗi khác')
                
                messages.success(request, msg)
                # Render lại form với thông báo thành công (không redirect)
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
                
            except Exception as e:
                messages.error(request, f' Lỗi: {str(e)}')
                batch.delete()
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
        
        else:
            # ===== TẠO PHIẾU BÌNH THƯỜNG =====
            if form.is_valid():
                batch = form.save(commit=False)
                batch.created_by = request.user
                if not batch.batch_number:
                    batch.batch_number = generate_batch_number(batch.batch_type)
                batch.save()
                messages.success(request, ' Phiếu đã được tạo! Hãy thêm sản phẩm.')
                return redirect('dashboard:warehouse_batch_add_items', pk=batch.pk)
    else:
        form = WarehouseBatchForm()
    
    return render(request, 'dashboard/warehouse/batch_form.html', {
        'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
    })

@admin_required
def warehouse_batch_add_items(request, pk):
    import traceback
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from dashboard.models import WarehouseBatch, WarehouseBatchItem
        from dashboard.forms import WarehouseBatchItemForm
        
        batch = get_object_or_404(WarehouseBatch, pk=pk)
        if request.method == 'POST':
            form = WarehouseBatchItemForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.batch = batch
                item.save()
                
                # Cập nhật tồn kho
                warehouse_item = item.warehouse_item
                if batch.batch_type == 'import':
                    warehouse_item.quantity += item.quantity
                else:
                    warehouse_item.quantity -= item.quantity
                warehouse_item.save()
                
                # Cập nhật tổng tiền của phiếu
                batch.calculate_total()
                batch.save()
                
                messages.success(request, 'Sản phẩm đã được thêm vào phiếu!')
                return redirect('dashboard:warehouse_batch_add_items', pk=batch.pk)
        else:
            form = WarehouseBatchItemForm()
        
        # Tính tổng tiền trước khi render
        batch.calculate_total()
        
        return render(request, 'dashboard/warehouse/batch_add_items.html', {
            'batch': batch,
            'form': form,
            'page_title': f'Thêm Sản Phẩm - Phiếu {batch.batch_number}',
        })
    except Exception as e:
        logger.error(f'Error in warehouse_batch_add_items: {str(e)}')
        logger.error(traceback.format_exc())
        raise

@admin_required
def warehouse_batch_detail(request, pk):
    from dashboard.models import WarehouseBatch
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    
    # Tính tổng tiền trước khi render
    batch.calculate_total()
    
    return render(request, 'dashboard/warehouse/batch_detail.html', {
        'batch': batch, 'page_title': f'Phiếu {batch.batch_number}',
    })

@admin_required
def warehouse_batch_print(request, pk):
    from dashboard.models import WarehouseBatch
    from dashboard.utils import export_batch_to_pdf
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    
    # Tính tổng tiền trước khi in
    batch.calculate_total()
    
    # Cập nhật trạng thái in
    from django.utils import timezone
    batch.is_printed = True
    batch.printed_at = timezone.now()
    batch.save()
    
    return export_batch_to_pdf(batch)

@admin_required  
def warehouse_batch_export_excel(request, pk):
    from dashboard.models import WarehouseBatch
    from dashboard.utils import export_batch_to_excel
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    
    # Tính tổng tiền trước khi export
    batch.calculate_total()
    
    wb = export_batch_to_excel(batch)
    if wb is None:
        messages.error(request, 'openpyxl chưa được cài đặt. Vui lòng cài đặt bằng pip install openpyxl')
        return redirect('dashboard:warehouse_batch_detail', pk=batch.pk)
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="phieu_{batch.batch_number}.xlsx"'
    wb.save(response)
    return response

@admin_required
def warehouse_batch_template_excel(request, warehouse_id):
    """Download Excel template cho import dữ liệu"""
    from dashboard.models import Warehouse
    from dashboard.utils import generate_excel_template
    
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    
    wb = generate_excel_template(warehouse)
    if wb is None:
        messages.error(request, 'Lỗi: openpyxl chưa được cài đặt hoặc lỗi tạo template')
        return redirect('dashboard:warehouse_batch_create')
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="template_import_{warehouse.store.name}.xlsx"'
    wb.save(response)
    return response

@admin_required
@require_http_methods(["POST"])
def warehouse_batch_delete(request, pk):
    from dashboard.models import WarehouseBatch
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    batch.delete()
    messages.success(request, 'Phiếu đã được xóa!')
    return redirect('dashboard:warehouse_batch_list')


# ==================== WAREHOUSE BATCH ITEM MANAGEMENT ====================
@admin_required
def warehouse_batch_item_delete(request, pk):
    from dashboard.models import WarehouseBatchItem
    item = get_object_or_404(WarehouseBatchItem, pk=pk)
    batch = item.batch
    
    # Hoàn tác số lượng tồn kho
    warehouse_item = item.warehouse_item
    if batch.batch_type == 'import':
        warehouse_item.quantity -= item.quantity
    else:
        warehouse_item.quantity += item.quantity
    warehouse_item.save()
    
    item.delete()
    
    # Cập nhật tổng tiền của phiếu
    batch.calculate_total()
    batch.save()
    
    messages.success(request, 'Sản phẩm đã được xóa khỏi phiếu!')
    return redirect('dashboard:warehouse_batch_add_items', pk=batch.pk)

@admin_required
def warehouse_import_excel(request):
    from dashboard.models import Warehouse
    from dashboard.forms import ImportExcelForm
    from dashboard.utils import import_warehouse_from_excel
    
    if request.method == 'POST':
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES.get('excel_file')
            warehouse = form.cleaned_data['warehouse']
            supplier = form.cleaned_data.get('supplier', '')
            
            result = import_warehouse_from_excel(excel_file, warehouse, supplier)
            if result['success']:
                messages.success(request, f"Đã nhập {result['items_added']} sản phẩm. Phiếu: {result['batch_number']}")
                if result['errors']:
                    for error in result['errors']:
                        messages.warning(request, error)
                return redirect('dashboard:warehouse_batch_detail', pk=result['batch_id'])
            else:
                messages.error(request, f"Lỗi: {result['error']}")
    else:
        form = ImportExcelForm()
    
    return render(request, 'dashboard/warehouse/import_excel.html', {
        'form': form,
        'page_title': 'Nhập Kho Từ Excel',
    })


# ==================== SEARCH API ====================
@api_view(['GET'])
def api_search_stores(request):
    """API tìm cửa hàng theo tên hoặc địa chỉ"""
    from dashboard.utils import search_stores_by_location
    
    query = request.GET.get('q', '').strip()
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lng')
    radius = float(request.GET.get('radius', 5))  # km
    
    stores = Store.objects.all()
    
    # Tìm kiếm theo tên hoặc địa chỉ
    if query:
        stores = search_items(stores, query, ['name', 'address'])
    
    # Tìm kiếm theo vị trí địa lý
    if latitude and longitude:
        try:
            lat = float(latitude)
            lng = float(longitude)
            nearby = search_stores_by_location(lat, lng, radius)
            result_data = [{
                'id': item['store'].id,
                'name': item['store'].name,
                'address': item['store'].address,
                'latitude': item['store'].latitude,
                'longitude': item['store'].longitude,
                'distance': item['distance'],
                'opening_hours': item['store'].opening_hours,
            } for item in nearby]
            return Response(result_data)
        except ValueError:
            return Response({'error': 'Vĩ độ/Kinh độ không hợp lệ'}, status=400)
    
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_search_by_alley(request):
    """API tìm cửa hàng trong hẻm/con hẻm"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': 'Vui lòng nhập từ khóa tìm kiếm'}, status=400)
    
    stores = Store.objects.all()
    results = search_items(stores, query, ['address'])
    
    serializer = StoreSerializer(results, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_warehouse_low_stock(request):
    """API lấy danh sách sản phẩm tồn kho thấp"""
    from dashboard.models import WarehouseItem
    
    warehouse_id = request.GET.get('warehouse_id')
    low_stock = WarehouseItem.objects.filter(quantity__lte=models.F('min_quantity'))
    
    if warehouse_id:
        low_stock = low_stock.filter(warehouse_id=warehouse_id)
    
    data = [{
        'id': item.id,
        'product': item.product.name,
        'warehouse': item.warehouse.store.name,
        'quantity': item.quantity,
        'min_quantity': item.min_quantity,
        'unit': item.unit,
    } for item in low_stock.select_related('product', 'warehouse__store')]
    
    return Response(data)


# ==================== API (DRF) ====================
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user and request.user.is_staff

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAdminOrReadOnly]

@api_view(['GET', 'POST'])
def store_list_create(request):
    if request.method == 'GET':
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer


# ==================== ABOUT MANAGEMENT ====================
@admin_required
def about_list(request):
    """Display list of About articles"""
    articles = About.objects.all().order_by('order', '-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        articles = articles.filter(status=status_filter)
    
    # Get page number from request
    page = request.GET.get('page', 1)
    articles, paginator = paginate_queryset(articles, page)
    
    context = {
        'articles': articles,
        'page_title': 'Quản Lý Trang Giới Thiệu',
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/about/list.html', context)


@admin_required
def about_create(request):
    """Create new About article"""
    if request.method == 'POST':
        form = AboutForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, '✅ Bài viết giới thiệu đã được tạo thành công!')
            return redirect('dashboard:about_list')
    else:
        form = AboutForm()
    
    context = {
        'form': form,
        'page_title': 'Tạo Bài Viết Giới Thiệu Mới',
        'action': 'create',
    }
    return render(request, 'dashboard/about/form.html', context)


@admin_required
def about_edit(request, pk):
    """Edit existing About article"""
    article = get_object_or_404(About, pk=pk)
    
    if request.method == 'POST':
        form = AboutForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Bài viết giới thiệu đã được cập nhật thành công!')
            return redirect('dashboard:about_list')
    else:
        form = AboutForm(instance=article)
    
    context = {
        'form': form,
        'article': article,
        'page_title': f'Chỉnh Sửa Bài Viết: {article.title}',
        'action': 'edit',
    }
    return render(request, 'dashboard/about/form.html', context)


@admin_required
def about_delete(request, pk):
    """Delete About article"""
    article = get_object_or_404(About, pk=pk)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, '✅ Bài viết giới thiệu đã được xóa thành công!')
        return redirect('dashboard:about_list')
    
    context = {
        'article': article,
        'page_title': 'Xóa Bài Viết Giới Thiệu',
    }
    return render(request, 'dashboard/about/delete.html', context)


@admin_required
def about_detail(request, pk):
    """View details of About article"""
    article = get_object_or_404(About, pk=pk)
    
    context = {
        'article': article,
        'page_title': f'Chi Tiết: {article.title}',
    }
    return render(request, 'dashboard/about/detail.html', context)


@admin_required
def about_import(request):
    """Import content from Word file or external URL"""
    if request.method == 'POST':
        form = AboutImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_type = form.cleaned_data['import_type']
            
            if import_type == 'word':
                # Handle Word file import
                word_file = form.cleaned_data['word_file']
                try:
                    # TODO: Implement Word file parsing
                    # For now, create a placeholder article
                    article = About.objects.create(
                        title=f"Import from {word_file.name}",
                        slug=f"import-{word_file.name}",
                        content="Content imported from Word file",
                        source_type='word',
                        author=request.user,
                        status='draft'
                    )
                    messages.success(request, '✅ File Word đã được nhập thành công!')
                    return redirect('dashboard:about_edit', pk=article.pk)
                except Exception as e:
                    messages.error(request, f'❌ Lỗi khi đọc file Word: {str(e)}')
            
            elif import_type == 'external':
                # Handle external URL import
                external_url = form.cleaned_data['external_url']
                try:
                    # TODO: Implement external URL content fetching
                    # For now, create a placeholder article
                    article = About.objects.create(
                        title=f"Import from {external_url}",
                        slug=f"import-{external_url.replace('https://', '').replace('/', '-')}",
                        content=f"Content imported from: {external_url}",
                        external_link=external_url,
                        source_type='external',
                        author=request.user,
                        status='draft'
                    )
                    messages.success(request, '✅ Nội dung từ URL đã được nhập thành công!')
                    return redirect('dashboard:about_edit', pk=article.pk)
                except Exception as e:
                    messages.error(request, f'❌ Lỗi khi lấy nội dung từ URL: {str(e)}')
    else:
        form = AboutImportForm()
    
    context = {
        'form': form,
        'page_title': 'Nhập Bài Viết Từ Nguồn Bên Ngoài',
    }
    return render(request, 'dashboard/about/import.html', context)


# ==================== CUSTOMER PROFILE ====================
def customer_profile_view(request):
    """View customer profile page"""
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để xem thông tin cá nhân.')
        return redirect('login')
    
    # Get or create customer profile
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
        'page_title': 'Thông Tin Cá Nhân',
    }
    return render(request, 'customer/profile.html', context)


def customer_profile_edit(request):
    """Edit customer profile"""
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để chỉnh sửa thông tin cá nhân.')
        return redirect('login')
    
    # Get or create customer profile
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserBasicInfoForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, '✅ Thông tin cá nhân đã được cập nhật thành công!')
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


# ==================== DASHBOARD CUSTOMER PROFILE MANAGEMENT ====================
@admin_required
def customer_profile_list(request):
    """Display list of all customer profiles for admin with statistics and advanced filtering"""
    profiles = CustomerProfile.objects.select_related('user').filter(pk__isnull=False).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        profiles = profiles.filter(
            models.Q(user__username__icontains=search_query) |
            models.Q(user__email__icontains=search_query) |
            models.Q(user__first_name__icontains=search_query) |
            models.Q(user__last_name__icontains=search_query) |
            models.Q(phone__icontains=search_query) |
            models.Q(address__icontains=search_query)
        )
    
    # Filter by verification status
    verified_filter = request.GET.get('verified', '')
    if verified_filter == 'verified':
        profiles = profiles.filter(is_verified=True)
    elif verified_filter == 'unverified':
        profiles = profiles.filter(is_verified=False)
    
    # Filter by account status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        profiles = profiles.filter(user__is_active=True)
    elif status_filter == 'inactive':
        profiles = profiles.filter(user__is_active=False)
    
    # Filter by gender
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        profiles = profiles.filter(gender=gender_filter)
    
    # Filter by VIP status
    vip_filter = request.GET.get('vip', '')
    if vip_filter == 'vip':
        profiles = profiles.filter(is_premium=True)
    elif vip_filter == 'normal':
        profiles = profiles.filter(is_premium=False)
    
    # Date range filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        profiles = profiles.filter(created_at__date__gte=date_from)
    if date_to:
        profiles = profiles.filter(created_at__date__lte=date_to)
    
    # Calculate statistics
    total_customers = CustomerProfile.objects.count()
    verified_count = CustomerProfile.objects.filter(is_verified=True).count()
    vip_count = CustomerProfile.objects.filter(is_premium=True).count()
    active_count = CustomerProfile.objects.filter(user__is_active=True).count()
    new_this_month = CustomerProfile.objects.filter(
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).count()
    
    # Calculate verification rate percentage
    verification_rate = 0
    if total_customers > 0:
        verification_rate = round((verified_count / total_customers) * 100, 1)
    
    # Pagination
    page = request.GET.get('page', 1)
    paginated_profiles = paginate_queryset(profiles, page, 20)
    
    context = {
        'profiles': paginated_profiles,
        'page_title': 'Quản Lý Thông Tin Người Dùng',
        'search_query': search_query,
        'verified_filter': verified_filter,
        'status_filter': status_filter,
        'gender_filter': gender_filter,
        'vip_filter': vip_filter,
        'date_from': date_from,
        'date_to': date_to,
        # Statistics
        'stats': {
            'total': total_customers,
            'verified': verified_count,
            'vip': vip_count,
            'active': active_count,
            'new_this_month': new_this_month,
            'verification_rate': verification_rate,
        },
        'gender_choices': CustomerProfile._meta.get_field('gender').choices,
    }
    return render(request, 'dashboard/customer_profiles/list.html', context)


@admin_required
def customer_profile_detail(request, pk):
    """Display detailed customer profile with order history and activity statistics"""
    profile = get_object_or_404(CustomerProfile, pk=pk)
    
    # Get customer's order history
    customer_orders = Order.objects.filter(user=profile.user).order_by('-created_at')[:10]
    
    # Calculate order statistics
    total_orders = Order.objects.filter(user=profile.user).count()
    total_spent = Order.objects.filter(user=profile.user).aggregate(
        total=models.Sum('total_price')
    )['total'] or 0
    
    # Calculate activity statistics
    orders_this_month = Order.objects.filter(
        user=profile.user,
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).count()
    
    # Get recent activity (last 5 orders with items)
    recent_orders_with_items = []
    for order in customer_orders[:5]:
        items = OrderItem.objects.filter(order=order).select_related('product')
        recent_orders_with_items.append({
            'order': order,
            'items': items,
            'item_count': items.count()
        })
    
    context = {
        'profile': profile,
        'page_title': f'Chi Tiết: {profile.display_name}',
        'customer_orders': customer_orders,
        'recent_orders_with_items': recent_orders_with_items,
        'order_stats': {
            'total_orders': total_orders,
            'total_spent': total_spent,
            'orders_this_month': orders_this_month,
        },
        'loyalty_points': profile.loyalty_points,
        'profile_completion': profile.get_completion_percentage(),
    }
    return render(request, 'dashboard/customer_profiles/detail.html', context)


@admin_required
def customer_profile_edit(request, pk):
    """Edit customer profile from dashboard"""
    profile = get_object_or_404(CustomerProfile, pk=pk)
    
    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserBasicInfoForm(request.POST, instance=profile.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            # Handle account status fields
            profile.user.is_active = request.POST.get('is_active') == 'on'
            profile.user.is_staff = request.POST.get('is_staff') == 'on'
            profile.is_verified = request.POST.get('is_verified') == 'on'
            
            profile_form.save()
            user_form.save()
            messages.success(request, f'✅ Thông tin người dùng {profile.display_name} đã được cập nhật thành công!')
            return redirect('dashboard:customer_profile_detail', pk=profile.pk)
        else:
            messages.error(request, '❌ Vui lòng sửa các lỗi bên dưới.')
    else:
        profile_form = CustomerProfileForm(instance=profile)
        user_form = UserBasicInfoForm(instance=profile.user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
        'page_title': f'Chỉnh Sửa: {profile.display_name}',
    }
    return render(request, 'dashboard/customer_profiles/edit.html', context)


@admin_required
def customer_profile_delete(request, pk):
    """Delete customer profile and associated user"""
    profile = get_object_or_404(CustomerProfile, pk=pk)
    user = profile.user
    
    if request.method == 'POST':
        username = profile.display_name
        profile.delete()
        user.delete()
        messages.success(request, f'✅ Người dùng {username} đã được xóa thành công!')
        return redirect('dashboard:customer_profile_list')
    
    context = {
        'profile': profile,
        'page_title': f'Xóa: {profile.display_name}',
    }
    return render(request, 'dashboard/customer_profiles/delete.html', context)


@admin_required
def customer_profile_toggle_verification(request, pk):
    """Toggle verification status of customer profile"""
    profile = get_object_or_404(CustomerProfile, pk=pk)
    profile.is_verified = not profile.is_verified
    profile.save()
    
    status = "xác thực" if profile.is_verified else "hủy xác thực"
    messages.success(request, f'✅ Đã {status} tài khoản của {profile.display_name}!')
    
    return redirect('dashboard:customer_profile_list')


# ==================== TIN TỨC (NEWS) ====================
@admin_required
def news_list(request):
    """List all news articles"""
    news_items = News.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        news_items = news_items.filter(status=status_filter)
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        news_items = news_items.filter(category=category_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        news_items = news_items.filter(title__icontains=search_query)
    
    context = {
        'news_items': news_items,
        'page_title': 'Quản Lý Tin Tức',
        'status_choices': News.STATUS_CHOICES,
        'category_choices': News.CATEGORY_CHOICES,
        'current_status': status_filter,
        'current_category': category_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/news/list.html', context)


@admin_required
def news_create(request):
    """Create new news article"""
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            if news.status == 'published' and not news.published_at:
                from django.utils import timezone
                news.published_at = timezone.now()
            news.save()
            messages.success(request, '✅ Tin tức đã được tạo thành công!')
            return redirect('dashboard:news_list')
        else:
            messages.error(request, '❌ Vui lòng sửa các lỗi bên dưới.')
    else:
        form = NewsForm()
    
    context = {
        'form': form,
        'page_title': 'Thêm Tin Tức Mới',
    }
    return render(request, 'dashboard/news/form.html', context)


@admin_required
def news_edit(request, pk):
    """Edit news article"""
    news = get_object_or_404(News, pk=pk)
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            news = form.save(commit=False)
            if news.status == 'published' and not news.published_at:
                from django.utils import timezone
                news.published_at = timezone.now()
            news.save()
            messages.success(request, '✅ Tin tức đã được cập nhật thành công!')
            return redirect('dashboard:news_list')
        else:
            messages.error(request, '❌ Vui lòng sửa các lỗi bên dưới.')
    else:
        form = NewsForm(instance=news)
    
    context = {
        'form': form,
        'news': news,
        'page_title': f'Sửa: {news.title}',
    }
    return render(request, 'dashboard/news/form.html', context)


@admin_required
def news_delete(request, pk):
    """Delete news article"""
    news = get_object_or_404(News, pk=pk)
    
    if request.method == 'POST':
        title = news.title
        news.delete()
        messages.success(request, f'✅ Tin tức "{title}" đã được xóa thành công!')
        return redirect('dashboard:news_list')
    
    context = {
        'news': news,
        'page_title': f'Xóa: {news.title}',
    }
    return render(request, 'dashboard/news/delete.html', context)


@admin_required
def news_toggle_status(request, pk):
    """Toggle news publish status"""
    news = get_object_or_404(News, pk=pk)
    
    if news.status == 'published':
        news.status = 'draft'
        messages.success(request, f'✅ Tin tức "{news.title}" đã chuyển sang bản nháp!')
    else:
        news.status = 'published'
        if not news.published_at:
            from django.utils import timezone
            news.published_at = timezone.now()
        messages.success(request, f'✅ Tin tức "{news.title}" đã được xuất bản!')
    
    news.save()
    return redirect('dashboard:news_list')


@admin_required
def news_toggle_featured(request, pk):
    """Toggle news featured status"""
    news = get_object_or_404(News, pk=pk)
    news.is_featured = not news.is_featured
    news.save()
    
    status = "nổi bật" if news.is_featured else "bình thường"
    messages.success(request, f'✅ Tin tức "{news.title}" đã chuyển sang trạng thái {status}!')
    
    return redirect('dashboard:news_list')


# ==================== REVIEW MANAGEMENT ====================
@admin_required
def review_list(request):
    """List and manage all product reviews"""
    reviews = Review.objects.select_related('user', 'order_item__product', 'order_item__order').prefetch_related('images').all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        reviews = reviews.filter(status=status_filter)
    
    # Filter by rating
    rating_filter = request.GET.get('rating')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        reviews = reviews.filter(
            models.Q(content__icontains=search_query) |
            models.Q(user__username__icontains=search_query) |
            models.Q(order_item__product__name__icontains=search_query)
        )
    
    # Statistics
    stats = {
        'total': Review.objects.count(),
        'pending': Review.objects.filter(status='pending').count(),
        'approved': Review.objects.filter(status='approved').count(),
        'rejected': Review.objects.filter(status='rejected').count(),
        'avg_rating': Review.objects.filter(status='approved').aggregate(avg=models.Avg('rating'))['avg'] or 0,
    }
    
    context = {
        'reviews': reviews,
        'stats': stats,
        'page_title': 'Quản lý Đánh giá',
        'status_filter': status_filter,
        'rating_filter': rating_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/reviews/list.html', context)


@admin_required
def review_detail(request, pk):
    """View review details"""
    review = get_object_or_404(Review.objects.select_related('user', 'order_item__product', 'order_item__order'), pk=pk)
    
    if request.method == 'POST':
        # Handle admin reply
        reply_form = ReviewReplyForm(request.POST)
        if reply_form.is_valid():
            review.admin_reply = reply_form.cleaned_data['admin_reply']
            review.admin_reply_at = timezone.now()
            review.save()
            messages.success(request, '✅ Đã gửi phản hồi!')
            return redirect('dashboard:review_detail', pk=pk)
    else:
        reply_form = ReviewReplyForm(initial={'admin_reply': review.admin_reply})
    
    context = {
        'review': review,
        'reply_form': reply_form,
        'page_title': f'Đánh giá #{review.id}',
    }
    return render(request, 'dashboard/reviews/detail.html', context)


@admin_required
def review_approve(request, pk):
    """Approve a review"""
    review = get_object_or_404(Review, pk=pk)
    review.status = 'approved'
    review.save()
    messages.success(request, f'✅ Đã duyệt đánh giá #{review.id}!')
    return redirect('dashboard:review_list')


@admin_required
def review_reject(request, pk):
    """Reject a review"""
    review = get_object_or_404(Review, pk=pk)
    review.status = 'rejected'
    review.save()
    messages.success(request, f'✅ Đã từ chối đánh giá #{review.id}!')
    return redirect('dashboard:review_list')


@admin_required
def review_delete(request, pk):
    """Delete a review"""
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, '✅ Đã xóa đánh giá!')
        return redirect('dashboard:review_list')
    
    context = {
        'review': review,
        'page_title': 'Xóa đánh giá',
    }
    return render(request, 'dashboard/reviews/delete.html', context)


# ==================== ORDER REVIEWS ====================
@admin_required
def order_review_list(request):
    """List all order reviews"""
    order_reviews = OrderReview.objects.select_related('order', 'user').all().order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status')
    if status_filter:
        order_reviews = order_reviews.filter(status=status_filter)
    
    rating_filter = request.GET.get('rating')
    if rating_filter:
        order_reviews = order_reviews.filter(overall_rating=rating_filter)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        order_reviews = order_reviews.filter(
            models.Q(order__id__icontains=search_query) |
            models.Q(user__username__icontains=search_query) |
            models.Q(content__icontains=search_query)
        )
    
    # Pagination
    page_obj, paginator = paginate_queryset(order_reviews, request.GET.get('page'), 10)
    
    # Stats
    stats = {
        'total': OrderReview.objects.count(),
        'pending': OrderReview.objects.filter(status='pending').count(),
        'approved': OrderReview.objects.filter(status='approved').count(),
        'rejected': OrderReview.objects.filter(status='rejected').count(),
        'avg_rating': OrderReview.objects.filter(status='approved').aggregate(avg=models.Avg('overall_rating'))['avg'] or 0,
    }
    
    context = {
        'order_reviews': page_obj,
        'paginator': paginator,
        'stats': stats,
        'page_title': 'Quản lý Đánh giá Đơn hàng',
        'status_filter': status_filter,
        'rating_filter': rating_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/order_reviews/list.html', context)


@admin_required
def order_review_detail(request, pk):
    """View order review details"""
    order_review = get_object_or_404(
        OrderReview.objects.select_related('order', 'user'), 
        pk=pk
    )
    
    if request.method == 'POST':
        # Handle admin reply
        reply_content = request.POST.get('admin_reply')
        if reply_content:
            order_review.admin_reply = reply_content
            order_review.admin_reply_at = timezone.now()
            order_review.save()
            messages.success(request, '✅ Đã gửi phản hồi!')
            return redirect('dashboard:order_review_detail', pk=pk)
    
    context = {
        'order_review': order_review,
        'page_title': f'Đánh giá Đơn hàng #{order_review.order.id}',
    }
    return render(request, 'dashboard/order_reviews/detail.html', context)


@admin_required
def order_review_approve(request, pk):
    """Approve an order review"""
    order_review = get_object_or_404(OrderReview, pk=pk)
    order_review.status = 'approved'
    order_review.save()
    messages.success(request, f'✅ Đã duyệt đánh giá đơn hàng #{order_review.order.id}!')
    return redirect('dashboard:order_review_list')


@admin_required
def order_review_reject(request, pk):
    """Reject an order review"""
    order_review = get_object_or_404(OrderReview, pk=pk)
    order_review.status = 'rejected'
    order_review.save()
    messages.success(request, f'✅ Đã từ chối đánh giá đơn hàng #{order_review.order.id}!')
    return redirect('dashboard:order_review_list')


@admin_required
def order_review_delete(request, pk):
    """Delete an order review"""
    order_review = get_object_or_404(OrderReview, pk=pk)
    if request.method == 'POST':
        order_review.delete()
        messages.success(request, '✅ Đã xóa đánh giá đơn hàng!')
        return redirect('dashboard:order_review_list')
    
    context = {
        'order_review': order_review,
        'page_title': 'Xóa đánh giá đơn hàng',
    }
    return render(request, 'dashboard/order_reviews/delete.html', context)


# ==================== SHIPPER MANAGEMENT ====================
@admin_required
def shippers_list(request):
    """List all shippers"""
    shippers = Shipper.objects.select_related('user').all().order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status')
    if status_filter:
        shippers = shippers.filter(status=status_filter)
    
    active_filter = request.GET.get('is_active')
    if active_filter:
        shippers = shippers.filter(is_active=active_filter == '1')
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        shippers = shippers.filter(
            models.Q(user__username__icontains=search_query) |
            models.Q(user__first_name__icontains=search_query) |
            models.Q(user__last_name__icontains=search_query) |
            models.Q(phone__icontains=search_query) |
            models.Q(license_plate__icontains=search_query)
        )
    
    # Pagination
    page_obj, paginator = paginate_queryset(shippers, request.GET.get('page'), 10)
    
    # Stats
    stats = {
        'total': Shipper.objects.count(),
        'available': Shipper.objects.filter(status='available', is_active=True).count(),
        'busy': Shipper.objects.filter(status='busy', is_active=True).count(),
        'offline': Shipper.objects.filter(status='offline').count() + Shipper.objects.filter(is_active=False).count(),
    }
    
    context = {
        'shippers': page_obj,
        'paginator': paginator,
        'stats': stats,
        'page_title': 'Quản lý Shipper',
        'status_filter': status_filter,
        'active_filter': active_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/shippers/list.html', context)


@admin_required
def shipper_detail(request, pk):
    """View shipper details"""
    shipper = get_object_or_404(
        Shipper.objects.select_related('user'), 
        pk=pk
    )
    
    # Get delivery statistics
    active_deliveries = shipper.get_active_deliveries()
    completed_today = shipper.get_completed_deliveries_today()
    recent_deliveries = shipper.deliveries.select_related('order').order_by('-created_at')[:10]
    
    context = {
        'shipper': shipper,
        'active_deliveries': active_deliveries,
        'completed_today': completed_today,
        'recent_deliveries': recent_deliveries,
        'page_title': f'Chi tiết Shipper: {shipper.user.get_full_name() or shipper.user.username}',
    }
    return render(request, 'dashboard/shippers/detail.html', context)


@admin_required
def shipper_create(request):
    """Create new shipper"""
    if request.method == 'POST':
        # Get user data
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        # Shipper data
        phone = request.POST.get('phone')
        license_plate = request.POST.get('license_plate')
        vehicle_type = request.POST.get('vehicle_type')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create shipper
            shipper = Shipper.objects.create(
                user=user,
                phone=phone,
                license_plate=license_plate,
                vehicle_type=vehicle_type
            )
            
            messages.success(request, f'Đã tạo shipper {user.get_full_name() or user.username}!')
            return redirect('dashboard:shippers_list')
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    context = {
        'page_title': 'Thêm Shipper mới',
    }
    return render(request, 'dashboard/shippers/form.html', context)


@admin_required
def shipper_edit(request, pk):
    """Edit shipper"""
    shipper = get_object_or_404(Shipper.objects.select_related('user'), pk=pk)
    
    if request.method == 'POST':
        # Update user data
        user = shipper.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        
        # Update shipper data
        shipper.phone = request.POST.get('phone', shipper.phone)
        shipper.license_plate = request.POST.get('license_plate', shipper.license_plate)
        shipper.vehicle_type = request.POST.get('vehicle_type', shipper.vehicle_type)
        shipper.status = request.POST.get('status', shipper.status)
        shipper.is_active = request.POST.get('is_active') == 'on'
        shipper.save()
        
        messages.success(request, f'Đã cập nhật thông tin shipper!')
        return redirect('dashboard:shipper_detail', pk=pk)
    
    context = {
        'shipper': shipper,
        'page_title': f'Chỉnh sửa Shipper: {shipper.user.get_full_name() or shipper.user.username}',
    }
    return render(request, 'dashboard/shippers/form.html', context)


@admin_required
@require_http_methods(["POST"])
def shipper_delete(request, pk):
    """Delete shipper"""
    shipper = get_object_or_404(Shipper, pk=pk)
    name = shipper.user.get_full_name() or shipper.user.username
    
    # Delete user (cascade will delete shipper)
    shipper.user.delete()
    
    messages.success(request, f'Shipper "{name}" đã được xóa!')
    return redirect('dashboard:shippers_list')


@admin_required
def shipper_toggle_status(request, pk):
    """Toggle shipper active status"""
    shipper = get_object_or_404(Shipper, pk=pk)
    shipper.is_active = not shipper.is_active
    shipper.save()
    
    status = "kích hoạt" if shipper.is_active else "vô hiệu hóa"
    messages.success(request, f'Đã {status} shipper {shipper.user.get_full_name() or shipper.user.username}!')
    return redirect('dashboard:shippers_list')


# ==================== DELIVERY STATUS MANAGEMENT ====================
@admin_required
def delivery_status_list(request):
    """List all delivery statuses"""
    deliveries = DeliveryStatus.objects.select_related('order', 'shipper__user').all().order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    shipper_filter = request.GET.get('shipper')
    if shipper_filter:
        deliveries = deliveries.filter(shipper_id=shipper_filter)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        deliveries = deliveries.filter(
            models.Q(order__id__icontains=search_query) |
            models.Q(shipper__user__username__icontains=search_query) |
            models.Q(pickup_notes__icontains=search_query) |
            models.Q(delivery_notes__icontains=search_query)
        )
    
    # Pagination
    page_obj, paginator = paginate_queryset(deliveries, request.GET.get('page'), 10)
    
    # Get available shippers for filter
    shippers = Shipper.objects.filter(is_active=True).order_by('user__username')
    
    context = {
        'deliveries': page_obj,
        'paginator': paginator,
        'shippers': shippers,
        'page_title': 'Quản lý Trạng thái Giao hàng',
        'status_filter': status_filter,
        'shipper_filter': shipper_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/delivery_status/list.html', context)


@admin_required
def delivery_status_detail(request, pk):
    """View delivery status details"""
    delivery = get_object_or_404(
        DeliveryStatus.objects.select_related('order', 'shipper__user', 'order__user'), 
        pk=pk
    )
    
    context = {
        'delivery': delivery,
        'page_title': f'Chi tiết Giao hàng #{delivery.order.id}',
    }
    return render(request, 'dashboard/delivery_status/detail.html', context)


@admin_required
def delivery_status_assign(request, pk):
    """Assign shipper to delivery"""
    delivery = get_object_or_404(DeliveryStatus, pk=pk)
    
    if request.method == 'POST':
        shipper_id = request.POST.get('shipper')
        if shipper_id:
            shipper = get_object_or_404(Shipper, pk=shipper_id)
            delivery.shipper = shipper
            delivery.assigned_at = timezone.now()
            delivery.status = 'pending'  # Reset to pending
            delivery.save()
            
            # Update order
            delivery.order.shipper = shipper
            delivery.order.save()
            
            messages.success(request, f'Đã gán shipper {shipper.user.get_full_name() or shipper.user.username} cho đơn hàng #{delivery.order.id}!')
        else:
            messages.error(request, 'Vui lòng chọn shipper!')
        
        return redirect('dashboard:delivery_status_detail', pk=pk)
    
    # Get available shippers
    available_shippers = Shipper.objects.filter(
        status='available', 
        is_active=True
    ).order_by('user__username')
    
    context = {
        'delivery': delivery,
        'available_shippers': available_shippers,
        'page_title': f'Gán Shipper cho đơn hàng #{delivery.order.id}',
    }
    return render(request, 'dashboard/delivery_status/assign.html', context)
