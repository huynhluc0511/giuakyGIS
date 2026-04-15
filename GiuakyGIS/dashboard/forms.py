from django import forms
from django.contrib.auth.models import User
from dashboard.models import (
    Store, Product, Order, OrderItem, Category, Warehouse, WarehouseItem, 
    WarehouseTransaction, WarehouseBatch, WarehouseBatchItem
)


INPUT_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
SELECT_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address', 'latitude', 'longitude', 'opening_hours']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên cửa hàng'}),
            'address': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Địa chỉ chi tiết'}),
            'latitude': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Vĩ độ', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Kinh độ', 'step': '0.000001'}),
            'opening_hours': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '9:00 - 22:00'}),
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
            'lat': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.000001', 'placeholder': 'Vĩ độ', 'min': '0'}),
            'lng': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.000001', 'placeholder': 'Kinh độ', 'min': '0'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat')
        lng = cleaned_data.get('lng')
        
        if lat is not None and lat < 0:
            self.add_error('lat', 'Vĩ độ không được là số âm')
        if lng is not None and lng < 0:
            self.add_error('lng', 'Kinh độ không được là số âm')
        
        return cleaned_data


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


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['store', 'info']
        widgets = {
            'store': forms.Select(attrs={'class': SELECT_CLASS}),
            'info': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 8, 'placeholder': 'Nhập thông tin quản lý kho...'}),
        }


class WarehouseItemForm(forms.ModelForm):
    class Meta:
        model = WarehouseItem
        fields = ['warehouse', 'product', 'quantity', 'unit', 'min_quantity', 'unit_price']
        widgets = {
            'warehouse': forms.Select(attrs={'class': SELECT_CLASS}),
            'product': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng tồn'}),
            'unit': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'cái, kg, lít...'}),
            'min_quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tồn kho tối thiểu'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giá nhập', 'step': '0.01'}),
        }


class WarehouseTransactionForm(forms.ModelForm):
    class Meta:
        model = WarehouseTransaction
        fields = ['warehouse_item', 'transaction_type', 'quantity', 'unit_price', 'supplier', 'note']
        widgets = {
            'warehouse_item': forms.Select(attrs={'class': SELECT_CLASS}),
            'transaction_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Đơn giá', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhà cung cấp'}),
            'note': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Ghi chú'}),
        }


class WarehouseBatchForm(forms.ModelForm):
    class Meta:
        model = WarehouseBatch
        fields = ['warehouse', 'batch_type', 'batch_number', 'supplier', 'description']
        widgets = {
            'warehouse': forms.Select(attrs={'class': SELECT_CLASS}),
            'batch_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'batch_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số phiếu (tự động)'}),
            'supplier': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhà cung cấp/Người nhận'}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Mô tả chi tiết'}),
        }


class WarehouseBatchItemForm(forms.ModelForm):
    class Meta:
        model = WarehouseBatchItem
        fields = ['warehouse_item', 'quantity', 'unit_price']
        widgets = {
            'warehouse_item': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng', 'step': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Đơn giá', 'step': '0.01'}),
        }


class ImportExcelForm(forms.Form):
    """Form để tải lên file Excel import kho"""
    excel_file = forms.FileField(
        label='Tệp Excel',
        widget=forms.FileInput(attrs={'class': INPUT_CLASS, 'accept': '.xlsx,.xls,.csv'})
    )
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label='Kho hàng',
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    supplier = forms.CharField(
        max_length=255,
        label='Nhà cung cấp',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhà cung cấp'}),
        required=False
    )


class StoreSearchForm(forms.Form):
    """Form tìm kiếm cửa hàng theo tên hoặc địa chỉ"""
    query = forms.CharField(
        max_length=255,
        required=False,
        label='Tìm cửa hàng',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Tìm kiếm theo tên hoặc địa chỉ...'
        })
    )
    latitude = forms.FloatField(
        required=False,
        label='Vĩ độ',
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Vĩ độ (tùy chọn)',
            'step': '0.000001'
        })
    )
    longitude = forms.FloatField(
        required=False,
        label='Kinh độ',
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Kinh độ (tùy chọn)',
            'step': '0.000001'
        })
    )
