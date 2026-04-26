from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field


# ─── Custom User ────────────────────────────────────────────────────────────

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Öğrenci'),
        ('advisor', 'Danışman'),
    ]
    GENDER_CHOICES = [
        ('M', 'Erkek'),
        ('F', 'Kadın'),
        ('O', 'Diğer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=150, blank=True, null=True, verbose_name='Bölüm')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='Cinsiyet')
    # Advisor-specific fields (used only when role='advisor')
    branch = models.CharField(max_length=150, blank=True, null=True, verbose_name='Anabilim Dalı')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_advisor(self):
        return self.role == 'advisor'

    @property
    def is_student(self):
        return self.role == 'student'


# ─── Community ──────────────────────────────────────────────────────────────

class Community(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Topluluk Adı')
    description = CKEditor5Field(config_name='default', verbose_name='Açıklama', blank=True)
    director = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='directed_communities',
        verbose_name='Başkan',
        limit_choices_to={'role': 'student'},
    )
    advisor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='advised_communities',
        verbose_name='Danışman',
        limit_choices_to={'role': 'advisor'},
    )
    founded_date = models.DateField(auto_now_add=True, verbose_name='Kuruluş Tarihi')
    logo = models.ImageField(upload_to='community_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Topluluk'
        verbose_name_plural = 'Topluluklar'
        ordering = ['-founded_date']

    def __str__(self):
        return self.name


# ─── Community Creation Request (student -> advisor) ────────────────────────

class CommunityRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
    ]
    requester = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='community_requests',
        verbose_name='Talep Eden',
        limit_choices_to={'role': 'student'},
    )
    advisor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_requests',
        verbose_name='Danışman',
        limit_choices_to={'role': 'advisor'},
    )
    community_name = models.CharField(max_length=200, verbose_name='Topluluk Adı')
    community_description = CKEditor5Field(config_name='default', verbose_name='Açıklama', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True, verbose_name='Red Gerekçesi')

    class Meta:
        verbose_name = 'Topluluk Talebi'
        verbose_name_plural = 'Topluluk Talepleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.community_name} - {self.get_status_display()}"


# ─── Membership ─────────────────────────────────────────────────────────────

class Member(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Öğrenci',
        limit_choices_to={'role': 'student'},
    )
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE,
        related_name='members', verbose_name='Topluluk',
    )
    joined_date = models.DateField(auto_now_add=True, verbose_name='Üyelik Tarihi')

    class Meta:
        unique_together = ('student', 'community')
        verbose_name = 'Üye'
        verbose_name_plural = 'Üyeler'

    def __str__(self):
        return f"{self.student} → {self.community}"


# ─── Join Request (student -> community) ─────────────────────────────────────

class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
    ]
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='join_requests',
        limit_choices_to={'role': 'student'},
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='join_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'community')
        verbose_name = 'Üyelik Talebi'
        verbose_name_plural = 'Üyelik Talepleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} → {self.community} ({self.get_status_display()})"


# ─── Staff ──────────────────────────────────────────────────────────────────

class Staff(models.Model):
    TASK_CHOICES = [
        ('social_media', 'Sosyal Medya Ekibi'),
        ('sponsor', 'Sponsor Ekibi'),
        ('event', 'Etkinlik Ekibi'),
        ('pr', 'Halkla İlişkiler'),
        ('design', 'Tasarım Ekibi'),
        ('technical', 'Teknik Ekip'),
        ('other', 'Diğer'),
    ]
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='staff_roles',
        limit_choices_to={'role': 'student'},
    )
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name='staff_members',
    )
    task = models.CharField(max_length=20, choices=TASK_CHOICES, verbose_name='Görev')
    assigned_date = models.DateField(auto_now_add=True, verbose_name='Atanma Tarihi')

    class Meta:
        unique_together = ('student', 'community')
        verbose_name = 'Görevli'
        verbose_name_plural = 'Görevliler'

    def __str__(self):
        return f"{self.student} - {self.get_task_display()} ({self.community})"


# ─── Event ──────────────────────────────────────────────────────────────────

class Event(models.Model):
    LOCATION_CHOICES = [
        ('face', 'Yüz Yüze'),
        ('online', 'Online'),
    ]
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE,
        related_name='events', verbose_name='Topluluk',
    )
    title = models.CharField(max_length=300, verbose_name='Etkinlik Adı')
    description = CKEditor5Field(config_name='default', verbose_name='Açıklama')
    event_date = models.DateTimeField(verbose_name='Etkinlik Tarihi')
    location_type = models.CharField(
        max_length=6, choices=LOCATION_CHOICES,
        default='face', verbose_name='Tür',
    )
    location_detail = models.CharField(
        max_length=500, blank=True, null=True,
        verbose_name='Konum / Meet Linki',
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, related_name='created_events',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Etkinlik'
        verbose_name_plural = 'Etkinlikler'
        ordering = ['-event_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto deactivate if event date has passed
        if self.event_date and self.event_date < timezone.now():
            self.is_active = False
        super().save(*args, **kwargs)


# ─── Announcement ───────────────────────────────────────────────────────────

class Announcement(models.Model):
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE,
        related_name='announcements', verbose_name='Topluluk',
        null=True, blank=True,
    )
    title = models.CharField(max_length=300, verbose_name='Başlık')
    content = CKEditor5Field(config_name='announcement', verbose_name='İçerik')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, related_name='announcements',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_global = models.BooleanField(default=False, verbose_name='Genel Duyuru')

    class Meta:
        verbose_name = 'Duyuru'
        verbose_name_plural = 'Duyurular'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
