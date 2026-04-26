from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import CustomUser, Community, CommunityRequest, Event, Staff, Announcement, JoinRequest


# ─── Auth Forms ─────────────────────────────────────────────────────────────

class StudentRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Ad', widget=forms.TextInput(attrs={'placeholder': 'Adınız'}))
    last_name = forms.CharField(max_length=150, label='Soyad', widget=forms.TextInput(attrs={'placeholder': 'Soyadınız'}))
    email = forms.EmailField(label='E-posta', widget=forms.EmailInput(attrs={'placeholder': 'ornek@uni.edu.tr'}))
    department = forms.CharField(max_length=150, label='Bölüm', widget=forms.TextInput(attrs={'placeholder': 'Bilgisayar Mühendisliği'}))
    phone = forms.CharField(max_length=20, label='Telefon', required=False, widget=forms.TextInput(attrs={'placeholder': '05xx xxx xx xx'}))
    gender = forms.ChoiceField(choices=[('', '--- Seçiniz ---')] + list(CustomUser.GENDER_CHOICES), label='Cinsiyet', required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'department', 'phone', 'gender', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.department = self.cleaned_data.get('department')
        user.phone = self.cleaned_data.get('phone')
        user.gender = self.cleaned_data.get('gender')
        if commit:
            user.save()
        return user


class AdvisorRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Ad', widget=forms.TextInput(attrs={'placeholder': 'Adınız'}))
    last_name = forms.CharField(max_length=150, label='Soyad', widget=forms.TextInput(attrs={'placeholder': 'Soyadınız'}))
    email = forms.EmailField(label='E-posta', widget=forms.EmailInput(attrs={'placeholder': 'hoca@uni.edu.tr'}))
    department = forms.CharField(max_length=150, label='Bölüm', widget=forms.TextInput(attrs={'placeholder': 'Bilgisayar Mühendisliği'}))
    branch = forms.CharField(max_length=150, label='Anabilim Dalı', widget=forms.TextInput(attrs={'placeholder': 'Yazılım Mühendisliği'}))
    phone = forms.CharField(max_length=20, label='Telefon', required=False, widget=forms.TextInput(attrs={'placeholder': '05xx xxx xx xx'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'department', 'branch', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'advisor'
        user.department = self.cleaned_data.get('department')
        user.branch = self.cleaned_data.get('branch')
        user.phone = self.cleaned_data.get('phone')
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(label='Kullanıcı Adı', widget=forms.TextInput(attrs={'placeholder': 'Kullanıcı adınız'}))
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))


# ─── Community Forms ─────────────────────────────────────────────────────────

class CommunityRequestForm(forms.ModelForm):
    community_description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label='Topluluk Açıklaması',
        required=False,
    )

    class Meta:
        model = CommunityRequest
        fields = ['community_name', 'community_description', 'advisor']
        labels = {
            'community_name': 'Topluluk Adı',
            'advisor': 'Danışman Hoca',
        }
        widgets = {
            'community_name': forms.TextInput(attrs={'placeholder': 'Topluluk adı giriniz'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['advisor'].queryset = CustomUser.objects.filter(role='advisor')
        self.fields['advisor'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.department or obj.branch or '-'})"


# ─── Community Edit Form ─────────────────────────────────────────────────────

class CommunityEditForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label='Topluluk Açıklaması',
        required=False,
    )

    class Meta:
        model = Community
        fields = ['name', 'description', 'logo']
        labels = {
            'name': 'Topluluk Adı',
            'logo': 'Logo (opsiyonel)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Topluluk adı'}),
        }


# ─── Event Forms ─────────────────────────────────────────────────────────────

class EventForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label='Etkinlik Açıklaması',
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'location_type', 'location_detail']
        labels = {
            'title': 'Etkinlik Adı',
            'event_date': 'Etkinlik Tarihi & Saati',
            'location_type': 'Etkinlik Türü',
            'location_detail': 'Konum / Meet Linki',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Etkinlik adı'}),
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'location_detail': forms.TextInput(attrs={'placeholder': 'Adres veya online link'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_date'].input_formats = ['%Y-%m-%dT%H:%M']


# ─── Staff Forms ─────────────────────────────────────────────────────────────

class StaffAssignForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['student', 'task']
        labels = {
            'student': 'Üye',
            'task': 'Görev',
        }

    def __init__(self, *args, community=None, **kwargs):
        super().__init__(*args, **kwargs)
        if community:
            member_ids = community.members.values_list('student_id', flat=True)
            self.fields['student'].queryset = CustomUser.objects.filter(id__in=member_ids)
            self.fields['student'].label_from_instance = lambda obj: obj.get_full_name() or obj.username


# ─── Announcement Forms ──────────────────────────────────────────────────────

class AnnouncementForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditor5Widget(config_name='announcement'),
        label='Duyuru İçeriği',
    )

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_global']
        labels = {
            'title': 'Başlık',
            'is_global': 'Genel Duyuru (tüm kullanıcılara)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Duyuru başlığı'}),
        }


# ─── Profile Edit Form ───────────────────────────────────────────────────────

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'department', 'branch', 'phone', 'gender']
        labels = {
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-posta',
            'department': 'Bölüm',
            'branch': 'Anabilim Dalı',
            'phone': 'Telefon',
            'gender': 'Cinsiyet',
        }
