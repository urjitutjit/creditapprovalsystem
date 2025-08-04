from django.core.management.base import BaseCommand
from loans.models import Customer, Loan
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Generate sample customer and loan data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customers',
            type=int,
            default=10,
            help='Number of customers to create'
        )
        parser.add_argument(
            '--loans-per-customer',
            type=int,
            default=3,
            help='Number of loans per customer'
        )

    def handle(self, *args, **options):
        num_customers = options['customers']
        loans_per_customer = options['loans_per_customer']

        self.stdout.write(f'Creating {num_customers} customers with {loans_per_customer} loans each...')

        # Sample data
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Tom', 'Emma', 'Chris', 'Anna']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']

        customers_created = 0
        loans_created = 0

        for i in range(num_customers):
            # Create customer
            customer = Customer.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                age=random.randint(25, 65),
                phone_number=random.randint(9000000000, 9999999999),
                monthly_income=random.randint(30000, 150000),
                approved_limit=random.randint(500000, 5000000),
                current_debt=0
            )
            customers_created += 1

            # Create loans for this customer
            for j in range(loans_per_customer):
                loan_amount = random.randint(50000, 500000)
                tenure = random.randint(6, 60)
                interest_rate = random.uniform(8.0, 18.0)
                
                # Calculate EMI
                monthly_rate = (interest_rate / 100) / 12
                if monthly_rate > 0:
                    emi = loan_amount * monthly_rate * (1 + monthly_rate)**tenure
                    emi = emi / ((1 + monthly_rate)**tenure - 1)
                else:
                    emi = loan_amount / tenure

                # Random start date in the past
                start_date = date.today() - timedelta(days=random.randint(30, 1000))
                end_date = start_date + timedelta(days=tenure * 30)

                # Determine loan status and EMIs paid
                if end_date < date.today():
                    status = 'completed'
                    emis_paid = tenure
                else:
                    status = 'active'
                    emis_paid = random.randint(0, tenure)

                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    tenure=tenure,
                    interest_rate=interest_rate,
                    monthly_installment=emi,
                    emis_paid_on_time=emis_paid,
                    start_date=start_date,
                    end_date=end_date,
                    status=status
                )
                loans_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {customers_created} customers and {loans_created} loans!'
            )
        ) 