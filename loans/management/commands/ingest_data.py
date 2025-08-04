from django.core.management.base import BaseCommand
from loans.tasks import ingest_all_data
import os


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customer-file',
            type=str,
            help='Path to customer data Excel file',
            default='customer_data.xlsx'
        )
        parser.add_argument(
            '--loan-file',
            type=str,
            help='Path to loan data Excel file',
            default='loan_data.xlsx'
        )

    def handle(self, *args, **options):
        customer_file = options['customer_file']
        loan_file = options['loan_file']

        # Check if files exist
        if not os.path.exists(customer_file):
            self.stdout.write(
                self.style.ERROR(f'Customer file not found: {customer_file}')
            )
            return

        if not os.path.exists(loan_file):
            self.stdout.write(
                self.style.ERROR(f'Loan file not found: {loan_file}')
            )
            return

        self.stdout.write('Starting data ingestion...')
        
        # Run the ingestion task
        result = ingest_all_data.delay(customer_file, loan_file)
        result_data = result.get()

        if result_data['status'] == 'success':
            self.stdout.write(
                self.style.SUCCESS('Data ingestion completed successfully!')
            )
            self.stdout.write(f"Customer result: {result_data['customer_result']['message']}")
            self.stdout.write(f"Loan result: {result_data['loan_result']['message']}")
        else:
            self.stdout.write(
                self.style.ERROR(f'Data ingestion failed: {result_data["message"]}')
            ) 