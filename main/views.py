from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import (
    CustomUser, Community, CommunityRequest, Member,
    JoinRequest, Staff, Event, Announcement
)
from .forms import (
    StudentRegisterForm, AdvisorRegisterForm, LoginForm,
    CommunityRequestForm, CommunityEditForm, EventForm, StaffAssignForm,
    AnnouncementForm, ProfileEditForm
)
from .emails import (
    send_advisor_request_email, send_request_accepted_email,
    send_request_rejected_email, send_join_notification_email
)


# ─── Home ────────────────────────────────────────────────────────────────────

def home(request):
    recent_events = Event.objects.filter(is_active=True).order_by('-event_date')[:4]
    recent_announcements = Announcement.objects.order_by('-created_at')[:3]
    community_count = Community.objects.filter(is_active=True).count()
    event_count = Event.objects.count()
    member_count = Member.objects.count()
    ctx = {
        'recent_events': recent_events,
        'recent_announcements': recent_announcements,
        'community_count': community_count,
        'event_count': event_count,
        'member_count': member_count,
    }
    return render(request, 'index.html', ctx)


# ─── Auth ────────────────────────────────────────────────────────────────────

def register_choice(request):
    return render(request, 'auth/register_choice.html')


def register_student(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = StudentRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Hoş geldiniz! Hesabınız başarıyla oluşturuldu.')
        return redirect('home')
    return render(request, 'auth/register_student.html', {'form': form})


def register_advisor(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = AdvisorRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Hoş geldiniz! Danışman hesabınız oluşturuldu.')
        return redirect('home')
    return render(request, 'auth/register_advisor.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('home')


# ─── Profile ─────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    user = request.user
    memberships = user.memberships.select_related('community').all()
    directed = Community.objects.filter(director=user)
    advised = Community.objects.filter(advisor=user)
    pending_requests = CommunityRequest.objects.filter(advisor=user, status='pending') if user.is_advisor else None

    # Pending join requests: show to both directors AND advisors of a community
    pending_joins = []
    for comm in directed:
        pending_joins += list(comm.join_requests.filter(status='pending').select_related('student'))
    for comm in advised:
        # Avoid duplicates if somehow same community appears in both
        already_ids = {jr.pk for jr in pending_joins}
        pending_joins += [
            jr for jr in comm.join_requests.filter(status='pending').select_related('student')
            if jr.pk not in already_ids
        ]

    ctx = {
        'memberships': memberships,
        'directed': directed,
        'advised': advised,
        'pending_requests': pending_requests,
        'pending_joins': pending_joins,
    }
    return render(request, 'profile/profile.html', ctx)


@login_required
def profile_edit(request):
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Profiliniz güncellendi.')
        return redirect('profile')
    return render(request, 'profile/edit.html', {'form': form})


# ─── Communities ─────────────────────────────────────────────────────────────

def community_list(request):
    query = request.GET.get('q', '')
    communities = Community.objects.filter(is_active=True)
    if query:
        communities = communities.filter(Q(name__icontains=query))
    return render(request, 'communities/list.html', {'communities': communities, 'query': query})


def community_detail(request, pk):
    community = get_object_or_404(Community, pk=pk, is_active=True)
    members = community.members.select_related('student').all()
    staff = community.staff_members.select_related('student').all()
    events = community.events.filter(is_active=True).order_by('-event_date')[:5]
    announcements = community.announcements.order_by('-created_at')[:5]

    is_member = False
    is_director = False
    is_advisor = False
    has_pending_join = False
    if request.user.is_authenticated:
        is_member = community.members.filter(student=request.user).exists()
        is_director = community.director == request.user
        is_advisor = community.advisor == request.user
        has_pending_join = community.join_requests.filter(student=request.user, status='pending').exists()

    ctx = {
        'community': community,
        'members': members,
        'staff': staff,
        'events': events,
        'announcements': announcements,
        'is_member': is_member,
        'is_director': is_director,
        'is_advisor_of': is_advisor,
        'has_pending_join': has_pending_join,
    }
    return render(request, 'communities/detail.html', ctx)


@login_required
def community_create_request(request):
    if request.user.is_advisor:
        messages.error(request, 'Danışmanlar topluluk oluşturma talebinde bulunamaz.')
        return redirect('community_list')
    form = CommunityRequestForm(request.POST or None)
    if form.is_valid():
        comm_req = form.save(commit=False)
        comm_req.requester = request.user
        comm_req.save()
        send_advisor_request_email(comm_req.advisor, request.user, comm_req.community_name)
        messages.success(request, 'Talebiniz danışmana iletildi. Onay bekleyin.')
        return redirect('profile')
    return render(request, 'communities/create_request.html', {'form': form})


@login_required
def advisor_respond_request(request, req_id, action):
    """Danışmanın topluluk talebini kabul/reddetmesi."""
    comm_req = get_object_or_404(CommunityRequest, pk=req_id, advisor=request.user, status='pending')
    if action == 'accept':
        # Create community
        community = Community.objects.create(
            name=comm_req.community_name,
            description=comm_req.community_description,
            director=comm_req.requester,
            advisor=request.user,
        )
        # Auto-add director as member
        Member.objects.create(student=comm_req.requester, community=community)
        comm_req.status = 'accepted'
        comm_req.responded_at = timezone.now()
        comm_req.save()
        send_request_accepted_email(comm_req.requester, comm_req.community_name)
        messages.success(request, f'"{comm_req.community_name}" topluluğu başarıyla kuruldu.')
    elif action == 'reject':
        reason = request.POST.get('reason', '')
        comm_req.status = 'rejected'
        comm_req.responded_at = timezone.now()
        comm_req.rejection_reason = reason
        comm_req.save()
        send_request_rejected_email(comm_req.requester, comm_req.community_name, reason)
        messages.info(request, 'Talep reddedildi.')
    return redirect('profile')


@login_required
def join_community(request, pk):
    community = get_object_or_404(Community, pk=pk, is_active=True)
    if request.user.is_advisor:
        messages.error(request, 'Danışmanlar topluluğa üye olamaz.')
        return redirect('community_detail', pk=pk)
    if community.members.filter(student=request.user).exists():
        messages.info(request, 'Zaten bu topluluğun üyesiniz.')
        return redirect('community_detail', pk=pk)
    if community.join_requests.filter(student=request.user, status='pending').exists():
        messages.info(request, 'Üyelik talebiniz zaten beklemede.')
        return redirect('community_detail', pk=pk)
    JoinRequest.objects.create(student=request.user, community=community)
    if community.director:
        send_join_notification_email(community.director, request.user, community.name)
    messages.success(request, 'Üyelik talebiniz gönderildi.')
    return redirect('community_detail', pk=pk)


@login_required
def respond_join_request(request, req_id, action):
    join_req = get_object_or_404(JoinRequest, pk=req_id, status='pending')
    community = join_req.community
    if community.director != request.user and community.advisor != request.user:
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('profile')
    if action == 'accept':
        Member.objects.get_or_create(student=join_req.student, community=community)
        join_req.status = 'accepted'
        join_req.save()
        messages.success(request, f'{join_req.student.get_full_name()} topluluğa eklendi.')
    elif action == 'reject':
        join_req.status = 'rejected'
        join_req.save()
        messages.info(request, 'Üyelik talebi reddedildi.')
    return redirect('profile')


@login_required
def assign_staff(request, pk):
    community = get_object_or_404(Community, pk=pk)
    if community.director != request.user and community.advisor != request.user:
        messages.error(request, 'Yetkiniz yok.')
        return redirect('community_detail', pk=pk)
    form = StaffAssignForm(request.POST or None, community=community)
    if form.is_valid():
        staff = form.save(commit=False)
        staff.community = community
        staff.save()
        messages.success(request, 'Görev ataması yapıldı.')
        return redirect('community_detail', pk=pk)
    return render(request, 'communities/assign_staff.html', {'form': form, 'community': community})


@login_required
def community_edit(request, pk):
    """Başkan veya danışman topluluk bilgilerini düzenleyebilir."""
    community = get_object_or_404(Community, pk=pk)
    if community.director != request.user and community.advisor != request.user:
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('community_detail', pk=pk)
    form = CommunityEditForm(request.POST or None, request.FILES or None, instance=community)
    if form.is_valid():
        form.save()
        messages.success(request, 'Topluluk bilgileri güncellendi.')
        return redirect('community_detail', pk=pk)
    return render(request, 'communities/edit.html', {'form': form, 'community': community})


@login_required
def community_delete(request, pk):
    """Başkan veya danışman topluluğu tamamen silebilir (cascade)."""
    community = get_object_or_404(Community, pk=pk)
    if community.director != request.user and community.advisor != request.user:
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('community_detail', pk=pk)
    if request.method == 'POST':
        name = community.name
        community.delete()  # CASCADE: Member, JoinRequest, Staff, Event, Announcement
        messages.success(request, f'"{name}" topluluğu ve tüm ilgili kayıtlar silindi.')
        return redirect('community_list')
    return render(request, 'communities/confirm_delete.html', {'community': community})


@login_required
def leave_community(request, pk):
    """Üye topluluktan ayrılabilir. Başkan ayrılamaz."""
    community = get_object_or_404(Community, pk=pk, is_active=True)
    if request.user.is_advisor:
        messages.error(request, 'Danışmanlar topluluk üyesi olamaz, bu işlem geçerli değil.')
        return redirect('community_detail', pk=pk)
    if community.director == request.user:
        messages.error(request, 'Topluluk başkanı topluluktan ayrılamaz. Önce başkanlığı devredin.')
        return redirect('community_detail', pk=pk)
    membership = Member.objects.filter(student=request.user, community=community).first()
    if not membership:
        messages.info(request, 'Zaten bu topluluğun üyesi değilsiniz.')
        return redirect('community_detail', pk=pk)
    if request.method == 'POST':
        membership.delete()
        messages.success(request, f'"{community.name}" topluluğundan ayrıldınız.')
        return redirect('community_list')
    return render(request, 'communities/confirm_leave.html', {'community': community})


# ─── Events ──────────────────────────────────────────────────────────────────

def event_list(request):
    # Auto-deactivate past events
    Event.objects.filter(event_date__lt=timezone.now(), is_active=True).update(is_active=False)
    filter_type = request.GET.get('type', 'all')
    events = Event.objects.select_related('community')
    if filter_type == 'active':
        events = events.filter(is_active=True)
    elif filter_type == 'past':
        events = events.filter(is_active=False)
    return render(request, 'events/list.html', {'events': events, 'filter_type': filter_type})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/detail.html', {'event': event})


@login_required
def event_create(request, comm_pk):
    community = get_object_or_404(Community, pk=comm_pk, is_active=True)
    if community.director != request.user and community.advisor != request.user:
        messages.error(request, 'Etkinlik oluşturmak için yetkiniz yok.')
        return redirect('community_detail', pk=comm_pk)
    form = EventForm(request.POST or None)
    if form.is_valid():
        event = form.save(commit=False)
        event.community = community
        event.created_by = request.user
        event.save()
        messages.success(request, 'Etkinlik oluşturuldu.')
        return redirect('event_detail', pk=event.pk)
    return render(request, 'events/create.html', {'form': form, 'community': community})


# ─── Announcements ───────────────────────────────────────────────────────────

def announcement_list(request):
    announcements = Announcement.objects.select_related('community', 'created_by').order_by('-created_at')
    return render(request, 'announcements/list.html', {'announcements': announcements})


def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    return render(request, 'announcements/detail.html', {'announcement': announcement})


@login_required
def announcement_create(request, comm_pk=None):
    community = get_object_or_404(Community, pk=comm_pk) if comm_pk else None
    if community and community.director != request.user and community.advisor != request.user:
        messages.error(request, 'Duyuru oluşturmak için yetkiniz yok.')
        return redirect('community_detail', pk=comm_pk)
    form = AnnouncementForm(request.POST or None)
    if form.is_valid():
        ann = form.save(commit=False)
        ann.created_by = request.user
        ann.community = community
        ann.save()
        messages.success(request, 'Duyuru yayınlandı.')
        return redirect('announcement_list')
    return render(request, 'announcements/create.html', {'form': form, 'community': community})
