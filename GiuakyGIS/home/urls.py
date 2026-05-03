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
    
    # Customer Review System URLs
    path('don-hang-cua-toi/', views.my_orders, name='my_orders'),
    path('danh-gia-don-hang/<int:order_id>/', views.create_order_review, name='create_order_review'),
    path('danh-gia-san-pham/<int:order_item_id>/', views.create_product_review, name='create_product_review'),
    path('danh-gia-cua-toi/', views.my_reviews, name='my_reviews'),
    path('chinh-sua-danh-gia-don-hang/<int:review_id>/', views.edit_order_review, name='edit_order_review'),
    path('chinh-sua-danh-gia-san-pham/<int:review_id>/', views.edit_product_review, name='edit_product_review'),
    
    # New Order Rating System URLs
    path('rate-order/<int:order_id>/', views.rate_order, name='rate_order'),
    path('submit-review/<int:order_id>/', views.submit_order_review, name='submit_order_review'),
    path('edit-order-review/<int:review_id>/', views.edit_order_review, name='edit_order_review'),
    path('delete-review-image/<int:image_id>/', views.delete_review_image, name='delete_review_image'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('order-delivered/<int:order_id>/', views.order_delivered_notification, name='order_delivered_notification'),
    
    # Shipper URLs
    path('shipper/', views.shipper_dashboard, name='shipper_dashboard'),
    path('shipper/workspace/', views.shipper_workspace, name='shipper_workspace'),
    path('shipper/available-orders/', views.shipper_available_orders, name='shipper_available_orders'),
    path('shipper/accept-order/<int:delivery_id>/', views.shipper_accept_order, name='shipper_accept_order'),
    path('shipper/delivery/<int:delivery_id>/', views.shipper_delivery_detail, name='shipper_delivery_detail'),
    path('shipper/profile/', views.shipper_profile, name='shipper_profile'),
    path('shipper/history/', views.shipper_delivery_history, name='shipper_delivery_history'),
    path('api/shipper/location/', views.shipper_update_location, name='shipper_update_location'),
    path('api/shipper/toggle-status/', views.shipper_toggle_status, name='shipper_toggle_status'),
    path('api/shipper/stats/', views.shipper_stats_api, name='shipper_stats_api'),
    path('api/delivery/<int:delivery_id>/location/', views.delivery_location_api, name='delivery_location_api'),
    path('api/delivery/<int:delivery_id>/details/', views.delivery_details_api, name='delivery_details_api'),
    
    # Order API
    path('api/order/create/', views.api_create_order, name='api_create_order'),
]
