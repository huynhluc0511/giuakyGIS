from django import forms
from django.contrib.auth.models import User
from dashboard.models import (
    Store, Product, Order, OrderItem, Category, Warehouse, WarehouseItem, 
    WarehouseTransaction, WarehouseBatch, WarehouseBatchItem, About, CustomerProfile, News,
    Review, ReviewImage
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


class AboutForm(forms.ModelForm):
    """Form for managing About articles"""
    class Meta:
        model = About
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image', 
            'external_link', 'source_type', 'status', 'order', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'Tiêu đề bài viết'
            }),
            'slug': forms.TextInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'slug-tieu-de-bai-viet'
            }),
            'content': forms.Textarea(attrs={
                'class': INPUT_CLASS + ' min-h-[300px]', 
                'placeholder': 'Nội dung chi tiết bài viết...',
                'rows': 10
            }),
            'excerpt': forms.Textarea(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'Tóm tắt ngắn gọn về bài viết...',
                'rows': 3
            }),
            'featured_image': forms.FileInput(attrs={
                'class': INPUT_CLASS,
                'accept': 'image/*'
            }),
            'external_link': forms.URLInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'https://example.com/bai-viet'
            }),
            'source_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'order': forms.NumberInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': '0',
                'min': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['slug'].required = True


class AboutImportForm(forms.Form):
    """Form for importing content from external sources"""
    import_type = forms.ChoiceField(
        choices=[
            ('word', 'Từ file Word (.docx)'),
            ('external', 'Từ liên kết URL'),
        ],
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
        label='Loại nhập'
    )
    word_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': INPUT_CLASS,
            'accept': '.docx,.doc'
        }),
        label='File Word'
    )
    external_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'https://example.com/bai-viet'
        }),
        label='URL bài viết'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        import_type = cleaned_data.get('import_type')
        word_file = cleaned_data.get('word_file')
        external_url = cleaned_data.get('external_url')
        
        if import_type == 'word' and not word_file:
            raise forms.ValidationError('Vui lòng chọn file Word khi nhập từ file.')
        elif import_type == 'external' and not external_url:
            raise forms.ValidationError('Vui lòng nhập URL khi nhập từ liên kết.')
        
        return cleaned_data


# Customer Profile Forms
class CustomerProfileForm(forms.ModelForm):
    """Form for editing customer profile"""
    
    class Meta:
        model = CustomerProfile
        fields = [
            'phone', 'address', 'avatar', 'birth_date', 'gender', 
            'bio', 'website', 'facebook', 'instagram', 'twitter', 'linkedin',
            'preferred_language', 'email_notifications', 'sms_notifications'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập số điện thoại'}),
            'address': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Nhập địa chỉ'}),
            'avatar': forms.FileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
            'birth_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'gender': forms.Select(attrs={'class': SELECT_CLASS}),
            'bio': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': 'Viết tiểu sử về bản thân...'}),
            'website': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://website.com'}),
            'facebook': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://facebook.com/username'}),
            'instagram': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://instagram.com/username'}),
            'twitter': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://twitter.com/username'}),
            'linkedin': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://linkedin.com/in/username'}),
            'preferred_language': forms.Select(attrs={'class': SELECT_CLASS}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'phone': 'Số điện thoại',
            'address': 'Địa chỉ',
            'avatar': 'Ảnh đại diện',
            'birth_date': 'Ngày sinh',
            'gender': 'Giới tính',
            'bio': 'Tiểu sử',
            'website': 'Website cá nhân',
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'twitter': 'Twitter',
            'linkedin': 'LinkedIn',
            'preferred_language': 'Ngôn ngữ ưu tiên',
            'email_notifications': 'Nhận thông báo qua email',
            'sms_notifications': 'Nhận thông báo qua SMS',
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace(' ', '').replace('-', '').replace('+', '').isdigit():
            raise forms.ValidationError('Số điện thoại chỉ được chứa ký tự số.')
        return phone
    
    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website and not website.startswith(('http://', 'https://')):
            return f'https://{website}'
        return website
    
    def clean_facebook(self):
        facebook = self.cleaned_data.get('facebook')
        if facebook and not facebook.startswith(('http://', 'https://')):
            return f'https://{facebook}'
        return facebook
    
    def clean_instagram(self):
        instagram = self.cleaned_data.get('instagram')
        if instagram and not instagram.startswith(('http://', 'https://')):
            return f'https://{instagram}'
        return instagram
    
    def clean_twitter(self):
        twitter = self.cleaned_data.get('twitter')
        if twitter and not twitter.startswith(('http://', 'https://')):
            return f'https://{twitter}'
        return twitter
    
    def clean_linkedin(self):
        linkedin = self.cleaned_data.get('linkedin')
        if linkedin and not linkedin.startswith(('http://', 'https://')):
            return f'https://{linkedin}'
        return linkedin
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
        self.fields['address'].required = False
        self.fields['avatar'].required = False
        self.fields['birth_date'].required = False
        self.fields['gender'].required = False
        self.fields['bio'].required = False
        self.fields['website'].required = False
        self.fields['facebook'].required = False
        self.fields['instagram'].required = False
        self.fields['twitter'].required = False
        self.fields['linkedin'].required = False


class UserBasicInfoForm(forms.ModelForm):
    """Form for editing basic user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập tên'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập họ'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập email'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = True


class NewsForm(forms.ModelForm):
    """Form for creating and editing news articles"""
    
    class Meta:
        model = News
        fields = [
            'title', 'slug', 'summary', 'content', 'image', 'category',
            'status', 'is_featured', 'published_at', 'meta_description', 'meta_keywords'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Nhập tiêu đề tin tức'
            }),
            'slug': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'slug-tin-tuc'
            }),
            'summary': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'rows': 3,
                'placeholder': 'Tóm tắt ngắn gọn nội dung tin tức'
            }),
            'content': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'rows': 10,
                'placeholder': 'Nội dung chi tiết tin tức'
            }),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-2 focus:ring-indigo-500'}),
            'published_at': forms.DateTimeInput(attrs={
                'class': INPUT_CLASS,
                'type': 'datetime-local'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Mô tả SEO (tối đa 255 ký tự)'
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Từ khóa SEO, phân cách bằng dấu phẩy'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['summary'].required = False
        self.fields['image'].required = False
        self.fields['published_at'].required = False
        self.fields['meta_description'].required = False
        self.fields['meta_keywords'].required = False
        
        # Add help texts
        self.fields['slug'].help_text = 'URL thân thiện, chỉ chứa chữ cái, số và dấu gạng ngang'
        self.fields['is_featured'].help_text = 'Tin nổi bật sẽ hiển thị ở vị trí đầu tiên'
        self.fields['published_at'].help_text = 'Ngày giờ xuất bản tin tức (để trống để xuất bản ngay lập tức)'


# Review Forms
class ReviewForm(forms.ModelForm):
    """Form for customers to submit reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-radio'}),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Chia sẻ trải nghiệm của bạn về món ăn này...'
            }),
        }
        labels = {
            'rating': 'Đánh giá của bạn',
            'content': 'Nội dung đánh giá',
        }


class ReviewImageForm(forms.ModelForm):
    """Form for uploading review images"""
    
    class Meta:
        model = ReviewImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'accept': 'image/*',
            }),
        }
        labels = {
            'image': 'Hình ảnh',
        }


class ReviewReplyForm(forms.Form):
    """Form for admin to reply to reviews"""
    admin_reply = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Nhập phản hồi cho người dùng...'
        }),
        label='Phản hồi của cửa hàng',
        required=True
    )
