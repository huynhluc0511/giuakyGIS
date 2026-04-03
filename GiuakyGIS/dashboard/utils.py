from functools import wraps
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.db.models import Q


def admin_required(view_func):
    """Kiểm tra quyền admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect('/')
    return wrapper


def search_items(queryset, q, search_fields):
    if not q:
        return queryset
    query = Q()
    for field in search_fields:
        query |= Q(**{f"{field}__icontains": q})
    return queryset.filter(query)


def paginate_queryset(queryset, page, per_page=15):
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page)
    return page_obj, paginator


def get_stats():
    from dashboard.models import Store, Product, Order, Category
    from django.contrib.auth.models import User

    stats = {
        'total_stores': Store.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_users': User.objects.count(),
        'total_categories': Category.objects.count(),
        'pending_orders': Order.objects.filter(status='Pending').count(),
        'processing_orders': Order.objects.filter(status='Processing').count(),
        'delivered_orders': Order.objects.filter(status='Delivered').count(),
    }
    return stats
