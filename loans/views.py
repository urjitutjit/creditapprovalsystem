from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from decimal import Decimal
from django.db import connection

from .models import Customer, Loan
from .serializers import (
    RegisterCustomerSerializer, CheckEligibilitySerializer, 
    CreateLoanSerializer, LoanDetailSerializer, CustomerLoanListSerializer
)
from .services import LoanEligibilityService


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint to monitor application status
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Get basic stats
        customer_count = Customer.objects.count()
        loan_count = Loan.objects.count()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "stats": {
                "customers": customer_count,
                "loans": loan_count
            }
        }
        
        return Response(health_status, status=status.HTTP_200_OK)
        
    except Exception as e:
        health_status = {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        return Response(health_status, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_documentation(request):
    """
    API Documentation endpoint
    """
    documentation = {
        "title": "Credit Approval System API",
        "version": "1.0.0",
        "description": "A Django-based credit approval system API",
        "endpoints": {
            "health_check": {
                "method": "GET",
                "url": "/health",
                "description": "Health check endpoint"
            },
            "register": {
                "method": "POST",
                "url": "/register",
                "description": "Register a new customer",
                "request_body": {
                    "first_name": "string",
                    "last_name": "string", 
                    "age": "integer",
                    "monthly_income": "integer",
                    "phone_number": "integer"
                },
                "response": {
                    "customer_id": "integer",
                    "name": "string",
                    "age": "integer",
                    "monthly_income": "integer",
                    "approved_limit": "integer",
                    "phone_number": "integer"
                }
            },
            "check_eligibility": {
                "method": "POST",
                "url": "/check-eligibility",
                "description": "Check loan eligibility for a customer",
                "request_body": {
                    "customer_id": "integer",
                    "loan_amount": "decimal",
                    "interest_rate": "decimal",
                    "tenure": "integer"
                },
                "response": {
                    "customer_id": "integer",
                    "approval": "boolean",
                    "interest_rate": "decimal",
                    "corrected_interest_rate": "decimal",
                    "tenure": "integer",
                    "monthly_installment": "decimal"
                }
            },
            "create_loan": {
                "method": "POST",
                "url": "/create-loan",
                "description": "Create a new loan for an eligible customer",
                "request_body": {
                    "customer_id": "integer",
                    "loan_amount": "decimal",
                    "interest_rate": "decimal",
                    "tenure": "integer"
                },
                "response": {
                    "loan_id": "integer",
                    "customer_id": "integer",
                    "loan_approved": "boolean",
                    "message": "string",
                    "monthly_installment": "decimal"
                }
            },
            "view_loan": {
                "method": "GET",
                "url": "/view-loan/{loan_id}",
                "description": "View loan details by loan ID",
                "response": {
                    "loan_id": "integer",
                    "customer": "object",
                    "loan_amount": "decimal",
                    "interest_rate": "decimal",
                    "monthly_installment": "decimal",
                    "tenure": "integer"
                }
            },
            "view_customer_loans": {
                "method": "GET",
                "url": "/view-loans/{customer_id}",
                "description": "View all loans for a customer",
                "response": "array of loan objects"
            }
        },
        "credit_score_calculation": {
            "description": "Credit score is calculated based on:",
            "components": [
                "Past Loans Paid on Time (35% weight)",
                "Number of Loans Taken (25% weight)", 
                "Loan Activity in Current Year (25% weight)",
                "Loan Approved Volume (15% weight)"
            ]
        },
        "loan_approval_criteria": {
            "credit_score_50_plus": "Approve with any interest rate",
            "credit_score_30_to_50": "Approve with interest rate > 12%",
            "credit_score_10_to_30": "Approve with interest rate > 16%",
            "credit_score_below_10": "No approval",
            "current_emis_50_percent": "No approval if current EMIs > 50% of monthly salary"
        }
    }
    
    return Response(documentation, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer
    """
    serializer = RegisterCustomerSerializer(data=request.data)
    if serializer.is_valid():
        try:
            customer = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Failed to create customer: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility for a customer
    """
    serializer = CheckEligibilitySerializer(data=request.data)
    if serializer.is_valid():
        try:
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']
            
            result = LoanEligibilityService.check_eligibility(
                customer_id, loan_amount, interest_rate, tenure
            )
            
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to check eligibility: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_loan(request):
    """
    Create a new loan for a customer
    """
    serializer = CreateLoanSerializer(data=request.data)
    if serializer.is_valid():
        try:
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']
            
            # Check eligibility first
            eligibility_result = LoanEligibilityService.check_eligibility(
                customer_id, loan_amount, interest_rate, tenure
            )
            
            if not eligibility_result['approval']:
                return Response({
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': eligibility_result.get('message', 'Loan not approved'),
                    'monthly_installment': 0
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the loan
            customer = Customer.objects.get(customer_id=customer_id)
            
            # Calculate start and end dates
            start_date = date.today()
            end_date = date.today().replace(year=date.today().year + tenure // 12)
            
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=eligibility_result['corrected_interest_rate'],
                monthly_installment=eligibility_result['monthly_installment'],
                start_date=start_date,
                end_date=end_date,
                status='active'
            )
            
            return Response({
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved successfully',
                'monthly_installment': float(loan.monthly_installment)
            }, status=status.HTTP_201_CREATED)
            
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create loan: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details by loan ID
    """
    try:
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve loan: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """
    View all loans for a customer
    """
    try:
        # Check if customer exists
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Get all loans for the customer
        loans = Loan.objects.filter(customer_id=customer_id)
        serializer = CustomerLoanListSerializer(loans, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve customer loans: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
