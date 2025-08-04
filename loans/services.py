from decimal import Decimal
from datetime import datetime, date
from django.db.models import Sum, Count, Q
from .models import Customer, Loan


class CreditScoreService:
    """Service for calculating credit scores and loan eligibility"""
    
    @staticmethod
    def calculate_credit_score(customer_id):
        """
        Calculate credit score (0-100) based on historical loan data
        """
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return 0
        
        # Check if current loans exceed approved limit
        total_current_loans = customer.loans.filter(status='active').aggregate(
            total=Sum('loan_amount')
        )['total'] or 0
        
        if total_current_loans > customer.approved_limit:
            return 0
        
        # Get all historical loans for the customer
        all_loans = customer.loans.all()
        
        if not all_loans.exists():
            return 0
        
        # Calculate components
        past_loans_paid_on_time = CreditScoreService._calculate_past_loans_paid_on_time(all_loans)
        number_of_loans_taken = CreditScoreService._calculate_number_of_loans_taken(all_loans)
        loan_activity_current_year = CreditScoreService._calculate_loan_activity_current_year(all_loans)
        loan_approved_volume = CreditScoreService._calculate_loan_approved_volume(all_loans)
        
        # Calculate weighted credit score
        credit_score = (
            past_loans_paid_on_time * 0.35 +
            number_of_loans_taken * 0.25 +
            loan_activity_current_year * 0.25 +
            loan_approved_volume * 0.15
        )
        
        return min(100, max(0, credit_score))
    
    @staticmethod
    def _calculate_past_loans_paid_on_time(loans):
        """Calculate score based on past loans paid on time (0-35 points)"""
        completed_loans = loans.filter(status='completed')
        if not completed_loans.exists():
            return 0
        
        total_loans = completed_loans.count()
        on_time_loans = 0
        
        for loan in completed_loans:
            if loan.emis_paid_on_time >= loan.tenure:
                on_time_loans += 1
        
        percentage = (on_time_loans / total_loans) * 100
        return min(35, percentage)
    
    @staticmethod
    def _calculate_number_of_loans_taken(loans):
        """Calculate score based on number of loans taken (0-25 points)"""
        total_loans = loans.count()
        
        if total_loans == 0:
            return 0
        elif total_loans == 1:
            return 10
        elif total_loans == 2:
            return 15
        elif total_loans == 3:
            return 20
        else:
            return 25
    
    @staticmethod
    def _calculate_loan_activity_current_year(loans):
        """Calculate score based on loan activity in current year (0-25 points)"""
        current_year = datetime.now().year
        current_year_loans = loans.filter(start_date__year=current_year)
        
        if not current_year_loans.exists():
            return 0
        
        # Score based on number of loans in current year
        loan_count = current_year_loans.count()
        if loan_count == 1:
            return 15
        elif loan_count == 2:
            return 20
        else:
            return 25
    
    @staticmethod
    def _calculate_loan_approved_volume(loans):
        """Calculate score based on loan approved volume (0-15 points)"""
        total_volume = loans.aggregate(total=Sum('loan_amount'))['total'] or 0
        
        # Convert to lakhs for scoring
        volume_in_lakhs = float(total_volume) / 100000
        
        if volume_in_lakhs == 0:
            return 0
        elif volume_in_lakhs <= 10:
            return 5
        elif volume_in_lakhs <= 25:
            return 10
        else:
            return 15


class LoanEligibilityService:
    """Service for checking loan eligibility and calculating interest rates"""
    
    @staticmethod
    def check_eligibility(customer_id, loan_amount, interest_rate, tenure):
        """
        Check loan eligibility and return appropriate response
        """
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'tenure': tenure,
                'monthly_installment': 0,
                'message': 'Customer not found'
            }
        
        # Calculate credit score
        credit_score = CreditScoreService.calculate_credit_score(customer_id)
        
        # Check if current EMIs exceed 50% of monthly salary
        total_current_emis = customer.get_total_current_emis()
        if total_current_emis > (customer.monthly_income * 0.5):
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'tenure': tenure,
                'monthly_installment': 0,
                'message': 'Total current EMIs exceed 50% of monthly salary'
            }
        
        # Determine approval based on credit score
        approval, corrected_interest_rate = LoanEligibilityService._determine_approval(
            credit_score, interest_rate
        )
        
        # Calculate monthly installment
        monthly_installment = LoanEligibilityService._calculate_monthly_installment(
            loan_amount, corrected_interest_rate, tenure
        )
        
        return {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': monthly_installment
        }
    
    @staticmethod
    def _determine_approval(credit_score, interest_rate):
        """
        Determine loan approval and corrected interest rate based on credit score
        """
        if credit_score > 50:
            return True, interest_rate
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                return True, interest_rate
            else:
                return True, 12.0  # Minimum rate for this bracket
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                return True, interest_rate
            else:
                return True, 16.0  # Minimum rate for this bracket
        else:
            return False, interest_rate
    
    @staticmethod
    def _calculate_monthly_installment(loan_amount, interest_rate, tenure):
        """
        Calculate monthly installment using compound interest formula
        """
        from decimal import Decimal
        
        # Convert to Decimal for precise calculation
        loan_amount = Decimal(str(loan_amount))
        interest_rate = Decimal(str(interest_rate))
        tenure = int(tenure)
        
        if interest_rate == 0:
            return float(loan_amount / tenure)
        
        # Convert annual interest rate to monthly
        monthly_rate = (interest_rate / 100) / 12
        
        # EMI formula: P * r * (1 + r)^n / ((1 + r)^n - 1)
        if monthly_rate > 0:
            emi = loan_amount * monthly_rate * (1 + monthly_rate)**tenure
            emi = emi / ((1 + monthly_rate)**tenure - 1)
            return float(emi)
        else:
            return float(loan_amount / tenure) 