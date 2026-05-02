from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('do-uong/', views.do_uong_view, name='do_uong'),
    path('ga-chien/', views.ga_chien_view, name='ga_chien'),
    path('hamburger/', views.hamburger_view, name='hamburger'),
    path('khoai-tay/', views.khoai_tay_view, name='khoai_tay'),
    path('pizza/', views.pizza_view, name='pizza'),
    path('gio-hang/', views.gio_hang_view, name='gio_hang'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('lien-he/', views.lien_he_view, name='lien_he'),
    path('gioi-thieu/', views.gioi_thieu_view, name='gioi_thieu'),
    path('tinh-trang/', views.tinh_trang_view, name='tinh_trang'),
    path('tim-duong/', views.tim_duong, name='tim_duong'),
    path('403/', views.custom_403, name='403'),
    # Customer Profile URLs
    path('profile/', views.customer_profile_view, name='customer_profile'),
    path('profile/enhanced/', views.customer_profile_view_enhanced, name='customer_profile_enhanced'),
    path('profile/edit/', views.customer_profile_edit, name='customer_profile_edit'),
    
    # News URLs
    path('tin-tuc/', views.news_list_view, name='news_list'),
    path('tin-tuc/<slug:slug>/', views.news_detail_view, name='news_detail'),
    
    # API for Stores
    path('api/stores/', views.api_stores_list, name='api_stores_list'),
    path('api/stores/nearby/', views.api_nearby_stores, name='api_nearby_stores'),
    
    # Review URLs
    path('review/submit/<int:order_item_id>/', views.submit_review, name='submit_review'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('product/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    
    # Order API
    path('api/order/create/', views.api_create_order, name='api_create_order'),
]
