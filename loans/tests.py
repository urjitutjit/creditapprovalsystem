from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, datetime

from .models import Customer, Loan
from .services import CreditScoreService, LoanEligibilityService


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number=9876543210,
            monthly_income=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.customer_id, 1)

    def test_calculate_approved_limit(self):
        expected_limit = round((36 * 50000) / 100000) * 100000
        self.assertEqual(self.customer.calculate_approved_limit(), expected_limit)

    def test_get_total_current_emis(self):
        # Create a loan for the customer
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10.5,
            monthly_installment=8791.59,
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1),
            status='active'
        )
        
        total_emis = self.customer.get_total_current_emis()
        self.assertEqual(float(total_emis), 8791.59)


class LoanModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number=9876543210,
            monthly_income=50000,
            approved_limit=1800000,
            current_debt=0
        )
        
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10.5,
            monthly_installment=8791.59,
            emis_paid_on_time=6,
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1),
            status='active'
        )

    def test_loan_creation(self):
        self.assertEqual(self.loan.loan_id, 1)
        self.assertEqual(self.loan.customer, self.customer)

    def test_repayments_left(self):
        self.assertEqual(self.loan.repayments_left, 6)  # 12 - 6 = 6

    def test_calculate_monthly_installment(self):
        # Test EMI calculation
        emi = self.loan.calculate_monthly_installment()
        self.assertGreater(emi, 0)


class CreditScoreServiceTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number=9876543210,
            monthly_income=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_calculate_credit_score_no_loans(self):
        score = CreditScoreService.calculate_credit_score(self.customer.customer_id)
        self.assertEqual(score, 0)

    def test_calculate_credit_score_with_loans(self):
        # Create completed loans
        for i in range(3):
            Loan.objects.create(
                customer=self.customer,
                loan_amount=100000,
                tenure=12,
                interest_rate=10.5,
                monthly_installment=8791.59,
                emis_paid_on_time=12,  # All EMIs paid on time
                start_date=date.today().replace(year=date.today().year - 1),
                end_date=date.today().replace(year=date.today().year - 1, month=12),
                status='completed'
            )
        
        score = CreditScoreService.calculate_credit_score(self.customer.customer_id)
        self.assertGreater(score, 0)


class LoanEligibilityServiceTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number=9876543210,
            monthly_income=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_check_eligibility_no_credit_history(self):
        result = LoanEligibilityService.check_eligibility(
            self.customer.customer_id, 100000, 10.5, 12
        )
        self.assertFalse(result['approval'])

    def test_check_eligibility_with_good_credit(self):
        # Create good credit history
        for i in range(2):
            Loan.objects.create(
                customer=self.customer,
                loan_amount=100000,
                tenure=12,
                interest_rate=10.5,
                monthly_installment=8791.59,
                emis_paid_on_time=12,
                start_date=date.today().replace(year=date.today().year - 1),
                end_date=date.today().replace(year=date.today().year - 1, month=12),
                status='completed'
            )
        
        result = LoanEligibilityService.check_eligibility(
            self.customer.customer_id, 100000, 10.5, 12
        )
        self.assertTrue(result['approval'])


class APITest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number=9876543210,
            monthly_income=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_register_customer(self):
        url = reverse('register_customer')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'age': 25,
            'monthly_income': 40000,
            'phone_number': 9876543211
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Jane Smith')
        self.assertIn('approved_limit', response.data)

    def test_check_eligibility(self):
        url = reverse('check_eligibility')
        data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 100000,
            'interest_rate': 10.5,
            'tenure': 12
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)

    def test_create_loan(self):
        # First create good credit history
        for i in range(2):
            Loan.objects.create(
                customer=self.customer,
                loan_amount=100000,
                tenure=12,
                interest_rate=10.5,
                monthly_installment=8791.59,
                emis_paid_on_time=12,
                start_date=date.today().replace(year=date.today().year - 1),
                end_date=date.today().replace(year=date.today().year - 1, month=12),
                status='completed'
            )
        
        url = reverse('create_loan')
        data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 100000,
            'interest_rate': 10.5,
            'tenure': 12
        }
        
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['loan_approved'])

    def test_view_loan(self):
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10.5,
            monthly_installment=8791.59,
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1),
            status='active'
        )
        
        url = reverse('view_loan', kwargs={'loan_id': loan.loan_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], loan.loan_id)

    def test_view_customer_loans(self):
        # Create some loans for the customer
        for i in range(2):
            Loan.objects.create(
                customer=self.customer,
                loan_amount=100000,
                tenure=12,
                interest_rate=10.5,
                monthly_installment=8791.59,
                start_date=date.today(),
                end_date=date.today().replace(year=date.today().year + 1),
                status='active'
            )
        
        url = reverse('view_customer_loans', kwargs={'customer_id': self.customer.customer_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
