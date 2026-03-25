from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', TemplateView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('members/', TemplateView.as_view(template_name='members.html'), name='members'),
    path('members/<int:id>/', TemplateView.as_view(template_name='member-detail.html'), name='member-detail'),
    path('members/add/', TemplateView.as_view(template_name='member-form.html'), name='member-add'),
    path('members/<int:id>/edit/', TemplateView.as_view(template_name='member-form.html'), name='member-edit'),
    path('sacraments/', TemplateView.as_view(template_name='sacraments.html'), name='sacraments'),
    path('pledges/', TemplateView.as_view(template_name='pledges.html'), name='pledges'),
    path('payments/', TemplateView.as_view(template_name='payments.html'), name='payments'),
    path('reports/', TemplateView.as_view(template_name='reports.html'), name='reports'),
]