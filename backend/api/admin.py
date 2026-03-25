from django.contrib import admin
from .models import Member, Sacrament, Pledge, Payment

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'civil_status']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['civil_status', 'gender']

@admin.register(Sacrament)
class SacramentAdmin(admin.ModelAdmin):
    list_display = ['member', 'sacrament_type', 'date_received', 'officiant']
    list_filter = ['sacrament_type']
    search_fields = ['member__first_name', 'member__last_name']

@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount_promised', 'due_date', 'status', 'balance']
    list_filter = ['status']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pledge', 'amount', 'payment_date', 'payment_method']
    list_filter = ['payment_method']