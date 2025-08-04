import pandas as pd
from celery import shared_task
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from .models import Customer, Loan


@shared_task
def ingest_customer_data(file_path):
    """
    Ingest customer data from Excel file
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        customers_created = 0
        customers_updated = 0
        
        with transaction.atomic():
            for _, row in df.iterrows():
                customer_data = {
                    'customer_id': int(row['customer_id']),
                    'first_name': str(row['first_name']),
                    'last_name': str(row['last_name']),
                    'phone_number': int(row['phone_number']),
                    'monthly_income': int(row['monthly_salary']),
                    'approved_limit': int(row['approved_limit']),
                    'current_debt': int(row['current_debt']),
                    'age': 30,  # Default age since not in original data
                }
                
                # Try to update existing customer or create new one
                customer, created = Customer.objects.update_or_create(
                    customer_id=customer_data['customer_id'],
                    defaults=customer_data
                )
                
                if created:
                    customers_created += 1
                else:
                    customers_updated += 1
        
        return {
            'status': 'success',
            'message': f'Customer data ingested successfully. Created: {customers_created}, Updated: {customers_updated}',
            'customers_created': customers_created,
            'customers_updated': customers_updated
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to ingest customer data: {str(e)}'
        }


@shared_task
def ingest_loan_data(file_path):
    """
    Ingest loan data from Excel file
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        loans_created = 0
        loans_updated = 0
        
        with transaction.atomic():
            for _, row in df.iterrows():
                try:
                    # Get customer
                    customer = Customer.objects.get(customer_id=int(row['customer_id']))
                    
                    # Parse dates
                    start_date = pd.to_datetime(row['start_date']).date()
                    end_date = pd.to_datetime(row['end_date']).date()
                    
                    loan_data = {
                        'customer': customer,
                        'loan_id': int(row['loan_id']),
                        'loan_amount': Decimal(str(row['loan_amount'])),
                        'tenure': int(row['tenure']),
                        'interest_rate': Decimal(str(row['interest_rate'])),
                        'monthly_installment': Decimal(str(row['monthly_repayment'])),
                        'emis_paid_on_time': int(row['EMIs_paid_on_time']),
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': 'completed' if end_date < datetime.now().date() else 'active',
                    }
                    
                    # Try to update existing loan or create new one
                    loan, created = Loan.objects.update_or_create(
                        loan_id=loan_data['loan_id'],
                        defaults=loan_data
                    )
                    
                    if created:
                        loans_created += 1
                    else:
                        loans_updated += 1
                        
                except Customer.DoesNotExist:
                    # Skip loans for non-existent customers
                    continue
                except Exception as e:
                    # Log error but continue processing
                    print(f"Error processing loan {row.get('loan_id', 'unknown')}: {str(e)}")
                    continue
        
        return {
            'status': 'success',
            'message': f'Loan data ingested successfully. Created: {loans_created}, Updated: {loans_updated}',
            'loans_created': loans_created,
            'loans_updated': loans_updated
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to ingest loan data: {str(e)}'
        }


@shared_task
def ingest_all_data(customer_file_path, loan_file_path):
    """
    Ingest both customer and loan data
    """
    try:
        # Ingest customer data first
        customer_result = ingest_customer_data.delay(customer_file_path)
        customer_result = customer_result.get()
        
        if customer_result['status'] == 'error':
            return customer_result
        
        # Ingest loan data
        loan_result = ingest_loan_data.delay(loan_file_path)
        loan_result = loan_result.get()
        
        return {
            'status': 'success',
            'customer_result': customer_result,
            'loan_result': loan_result,
            'message': 'All data ingested successfully'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to ingest data: {str(e)}'
        } 