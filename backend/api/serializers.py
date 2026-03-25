from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Member, Sacrament, Pledge, Payment

class MemberSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Member
        fields = '__all__'

class SacramentSerializer(serializers.ModelSerializer):
    member_name = serializers.ReadOnlyField(source='member.full_name')
    
    class Meta:
        model = Sacrament
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PledgeSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    member_name = serializers.ReadOnlyField(source='member.full_name')
    total_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = Pledge
        fields = '__all__'
    
    def get_total_paid(self, obj):
        total = obj.payments.aggregate(serializers.models.Sum('amount'))['amount__sum']
        return total or 0

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']