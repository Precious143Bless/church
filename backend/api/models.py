from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Member(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    CIVIL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Divorced', 'Divorced'),
        ('Separated', 'Separated'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES)
    baptism_date = models.DateField(blank=True, null=True)
    confirmation_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['last_name', 'first_name']

class Sacrament(models.Model):
    SACRAMENT_TYPES = [
        ('Baptism', 'Baptism'),
        ('Confirmation', 'Confirmation'),
        ('First Communion', 'First Holy Communion'),
        ('Marriage', 'Marriage'),
        ('Last Rites', 'Last Rites'),
        ('Confession', 'Confession'),
        ('Holy Orders', 'Holy Orders'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sacraments')
    sacrament_type = models.CharField(max_length=50, choices=SACRAMENT_TYPES)
    date_received = models.DateField()
    officiant = models.CharField(max_length=200, help_text="Name of priest/bishop")
    church_location = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Specific fields for Baptism
    godfather = models.CharField(max_length=200, blank=True, null=True)
    godmother = models.CharField(max_length=200, blank=True, null=True)
    
    # Specific fields for Confirmation
    confirmation_name = models.CharField(max_length=100, blank=True, null=True)
    sponsor = models.CharField(max_length=200, blank=True, null=True)
    
    # Specific fields for Marriage
    spouse_name = models.CharField(max_length=200, blank=True, null=True)
    witnesses = models.TextField(blank=True, null=True, help_text="Names of witnesses, one per line")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.member.full_name} - {self.sacrament_type}"
    
    class Meta:
        ordering = ['-date_received']

class Pledge(models.Model):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Settled', 'Settled'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='pledges')
    amount_promised = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.balance:
            self.balance = self.amount_promised
        super().save(*args, **kwargs)
    
    def update_status(self):
        if self.balance <= 0:
            self.status = 'Settled'
        elif self.balance < self.amount_promised:
            self.status = 'Partially Paid'
        else:
            self.status = 'Unpaid'
        self.save()
    
    def __str__(self):
        return f"{self.member.full_name} - ₱{self.amount_promised}"
    
    class Meta:
        ordering = ['-due_date']

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Check', 'Check'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Online', 'Online'),
    ]
    
    pledge = models.ForeignKey(Pledge, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update pledge balance
        total_paid = self.pledge.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.pledge.balance = self.pledge.amount_promised - total_paid
        self.pledge.update_status()
    
    def __str__(self):
        return f"Payment for {self.pledge.member.full_name} - ₱{self.amount}"
    
    class Meta:
        ordering = ['-payment_date']