from django.urls import path
from . import views

urlpatterns = [
    # ── Home ──────────────────────────────────────────────────────────────
    path('', views.home, name='home'),

    # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/register/', views.register_choice, name='register_choice'),
    path('auth/register/student/', views.register_student, name='register_student'),
    path('auth/register/advisor/', views.register_advisor, name='register_advisor'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    # ── Profile ───────────────────────────────────────────────────────────
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # ── Communities ───────────────────────────────────────────────────────
    path('communities/', views.community_list, name='community_list'),
    path('communities/<int:pk>/', views.community_detail, name='community_detail'),
    path('communities/request/', views.community_create_request, name='community_create_request'),
    path('communities/<int:pk>/join/', views.join_community, name='join_community'),
    path('communities/<int:pk>/leave/', views.leave_community, name='leave_community'),
    path('communities/<int:pk>/edit/', views.community_edit, name='community_edit'),
    path('communities/<int:pk>/delete/', views.community_delete, name='community_delete'),
    path('communities/<int:pk>/staff/', views.assign_staff, name='assign_staff'),
    path('communities/<int:comm_pk>/events/new/', views.event_create, name='event_create'),
    path('communities/<int:comm_pk>/announcements/new/', views.announcement_create, name='announcement_create'),

    # ── Advisor respond ───────────────────────────────────────────────────
    path('requests/<int:req_id>/<str:action>/', views.advisor_respond_request, name='advisor_respond_request'),
    path('join-requests/<int:req_id>/<str:action>/', views.respond_join_request, name='respond_join_request'),

    # ── Events ────────────────────────────────────────────────────────────
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),

    # ── Announcements ─────────────────────────────────────────────────────
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
]