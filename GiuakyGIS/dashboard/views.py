from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib import messages

from dashboard.models import Store, Product, Order, OrderItem, Category
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer, StoreSerializer, OrderSerializer, CategorySerializer
from .forms import (
    StoreForm, ProductForm, OrderForm, CategoryForm, SearchForm, UserForm
)
from .utils import admin_required, search_items, paginate_queryset, get_stats


# ==================== DASHBOARD ====================
@admin_required
def dashboard_index(request):
    stats = get_stats()
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    recent_products = Product.objects.all().order_by('-id')[:5]
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
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
    page_obj, paginator = paginate_queryset(products, request.GET.get('page'), 15)
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
    orders = Order.objects.select_related('user').all().order_by('-created_at')
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        orders = search_items(orders, q, ['full_name', 'phone', 'address', 'user__username'])
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    page_obj, paginator = paginate_queryset(orders, request.GET.get('page'), 15)
    status_choices = Order.STATUS_CHOICES
    return render(request, 'dashboard/orders/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'status_choices': status_choices,
        'current_status': status_filter, 'page_title': 'Quản Lý Đơn Hàng',
    })

@admin_required
def orders_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product').all()
    return render(request, 'dashboard/orders/detail.html', {
        'order': order, 'items': items, 'page_title': f'Đơn Hàng #{order.id}',
    })

@admin_required
def orders_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đơn hàng đã được cập nhật!')
            return redirect('dashboard:orders_detail', pk=order.pk)
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


# ==================== USERS ====================
@admin_required
def users_list(request):
    users = User.objects.all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        users = search_items(users, q, ['username', 'email', 'first_name', 'last_name'])
    page_obj, paginator = paginate_queryset(users, request.GET.get('page'), 15)
    return render(request, 'dashboard/users/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'page_title': 'Quản Lý Người Dùng',
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
        'form': form, 'user_obj': user,
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


# ==================== MANAGE STORES LEGACY ====================
@admin_required
def manage_stores_view(request):
    return render(request, 'dashboard/manage_stores.html')


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
    permission_classes = [IsAdminOrReadOnly]
