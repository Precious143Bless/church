from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Member, Sacrament, Pledge, Payment
from .serializers import (
    MemberSerializer, SacramentSerializer, 
    PledgeSerializer, PaymentSerializer, UserSerializer
)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.filter(is_active=True)
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        return queryset

class SacramentViewSet(viewsets.ModelViewSet):
    queryset = Sacrament.objects.all()
    serializer_class = SacramentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        member_id = self.request.query_params.get('member_id', None)
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        return queryset

class PledgeViewSet(viewsets.ModelViewSet):
    queryset = Pledge.objects.all()
    serializer_class = PledgeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        member_id = self.request.query_params.get('member_id', None)
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        return queryset

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    total_members = Member.objects.filter(is_active=True).count()
    total_sacraments = Sacrament.objects.count()
    total_pledges = Pledge.objects.count()
    outstanding_pledges = Pledge.objects.filter(
        ~Q(status='Settled')
    ).aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Recent members
    recent_members = Member.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_members_data = MemberSerializer(recent_members, many=True).data
    
    # Upcoming due pledges
    upcoming_pledges = Pledge.objects.filter(
        status__in=['Unpaid', 'Partially Paid'],
        due_date__gte=datetime.now().date()
    ).order_by('due_date')[:5]
    upcoming_pledges_data = PledgeSerializer(upcoming_pledges, many=True).data
    
    # Sacraments by type
    sacrament_counts = Sacrament.objects.values('sacrament_type').annotate(
        count=Count('id')
    )
    
    return Response({
        'total_members': total_members,
        'total_sacraments': total_sacraments,
        'total_pledges': total_pledges,
        'outstanding_pledges': outstanding_pledges,
        'recent_members': recent_members_data,
        'upcoming_pledges': upcoming_pledges_data,
        'sacrament_counts': sacrament_counts,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_reports(request):
    report_type = request.query_params.get('type', 'members')
    
    if report_type == 'members':
        members = Member.objects.filter(is_active=True)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
    
    elif report_type == 'sacraments':
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        sacraments = Sacrament.objects.all()
        if start_date:
            sacraments = sacraments.filter(date_received__gte=start_date)
        if end_date:
            sacraments = sacraments.filter(date_received__lte=end_date)
        
        serializer = SacramentSerializer(sacraments, many=True)
        return Response(serializer.data)
    
    elif report_type == 'financial':
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        payments = Payment.objects.all()
        if start_date:
            payments = payments.filter(payment_date__gte=start_date)
        if end_date:
            payments = payments.filter(payment_date__lte=end_date)
        
        total_collected = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        total_pledged = Pledge.objects.filter(
            due_date__lte=datetime.now().date()
        ).aggregate(Sum('amount_promised'))['amount_promised__sum'] or 0
        
        return Response({
            'total_collected': total_collected,
            'total_pledged': total_pledged,
            'payments': PaymentSerializer(payments, many=True).data
        })
    
    return Response({'error': 'Invalid report type'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_sacraments(request, member_id):
    sacraments = Sacrament.objects.filter(member_id=member_id)
    serializer = SacramentSerializer(sacraments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_pledges(request, member_id):
    pledges = Pledge.objects.filter(member_id=member_id)
    serializer = PledgeSerializer(pledges, many=True)
    return Response(serializer.data)