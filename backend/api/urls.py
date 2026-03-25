from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'members', views.MemberViewSet)
router.register(r'sacraments', views.SacramentViewSet)
router.register(r'pledges', views.PledgeViewSet)
router.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('current-user/', views.current_user, name='current-user'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('reports/', views.generate_reports, name='reports'),
    path('member/<int:member_id>/sacraments/', views.member_sacraments, name='member-sacraments'),
    path('member/<int:member_id>/pledges/', views.member_pledges, name='member-pledges'),
]