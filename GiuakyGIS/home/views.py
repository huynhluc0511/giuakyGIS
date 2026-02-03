from django.shortcuts import render

def home_view(request):
    # Django sẽ tự tìm trong thư mục Templates của bạn
    return render(request, 'home.html')