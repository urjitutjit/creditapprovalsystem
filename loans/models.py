from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import math


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    phone_number = models.BigIntegerField(unique=True)
    monthly_income = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_approved_limit(self):
        """Calculate approved limit based on monthly income"""
        return round((36 * self.monthly_income) / 100000) * 100000

    def get_total_current_emis(self):
        """Get total current EMIs for the customer"""
        return self.loans.filter(status='active').aggregate(
            total=models.Sum('monthly_installment')
        )['total'] or 0


class Loan(models.Model):
    LOAN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
    ]

    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tenure = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = models.DecimalField(max_digits=15, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.name}"

    @property
    def repayments_left(self):
        """Calculate remaining EMIs"""
        if self.status == 'completed':
            return 0
        total_emis = self.tenure
        return max(0, total_emis - self.emis_paid_on_time)

    def calculate_monthly_installment(self):
        """Calculate monthly installment using compound interest formula"""
        if self.interest_rate == 0:
            return self.loan_amount / self.tenure
        
        # Convert annual interest rate to monthly
        monthly_rate = (self.interest_rate / 100) / 12
        
        # EMI formula: P * r * (1 + r)^n / ((1 + r)^n - 1)
        if monthly_rate > 0:
            emi = self.loan_amount * monthly_rate * (1 + monthly_rate)**self.tenure
            emi = emi / ((1 + monthly_rate)**self.tenure - 1)
            return emi
        else:
            return self.loan_amount / self.tenure

    def save(self, *args, **kwargs):
        if not self.monthly_installment:
            self.monthly_installment = self.calculate_monthly_installment()
        super().save(*args, **kwargs)
