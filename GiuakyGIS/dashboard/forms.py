from django import forms
from django.contrib.auth.models import User
from dashboard.models import Store, Product, Order, OrderItem, Category


INPUT_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
SELECT_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên cửa hàng'}),
            'address': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Địa chỉ chi tiết'}),
            'latitude': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Vĩ độ', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Kinh độ', 'step': '0.000001'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên danh mục'}),
            'slug': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'slug-danh-muc'}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'image', 'is_available']
        widgets = {
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên món ăn'}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': 'Mô tả món ăn'}),
            'price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giá tiền (VNĐ)', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'is_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-2 focus:ring-indigo-500'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'full_name', 'phone', 'address', 'status', 'total_price', 'lat', 'lng']
        widgets = {
            'user': forms.Select(attrs={'class': SELECT_CLASS}),
            'full_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Họ tên người nhận'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số điện thoại'}),
            'address': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Địa chỉ giao hàng'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'total_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01'}),
            'lat': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.000001', 'placeholder': 'Vĩ độ'}),
            'lng': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.000001', 'placeholder': 'Kinh độ'}),
        }


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Tìm kiếm...'
        })
    )


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Để trống nếu không đổi mật khẩu'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Họ'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600'}),
        }
