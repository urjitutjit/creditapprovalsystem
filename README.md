 Credit Approval System
A comprehensive Django-based credit approval system with REST API endpoints for customer registration, loan eligibility checking, and loan management.

🚀 Features
Customer Management – Register new customers with auto-approved limits

Credit Scoring – Dynamic scoring based on historical loan behavior

Loan Eligibility – Smart approval engine with interest rate adjustments

Loan Management – Track and manage EMIs and approvals

Background Tasks – Celery + Redis for Excel ingestion

Testing Suite – Full unit testing for logic & endpoints

Dockerized – Production-ready with PostgreSQL and Redis containers

🛠 Tech Stack
Layer	Tech Used
Backend	Django 4.2.7, Django REST Framework 3.14
Database	SQLite (Dev), PostgreSQL (Prod)
Task Queue	Celery 5.3.4, Redis 5.0.1
Data Handling	Pandas, OpenPyXL
Containerization	Docker, Docker Compose
Testing	Django TestCase, DRF APITestCase

📊 API Endpoints
1. Register Customer
POST /register
→ Registers a new customer
→ approved_limit = 36 × monthly_salary (rounded to nearest lakh)

2. Check Loan Eligibility
POST /check-eligibility
→ Evaluates loan eligibility based on credit score & business logic

3. Create Loan
POST /create-loan
→ Approves or rejects loan request

4. View Loan Details
GET /view-loan/{loan_id}
→ Returns loan + customer details

5. View Customer Loans
GET /view-loans/{customer_id}
→ Lists all loans for a customer

6. Health Check
GET /health
→ System diagnostics and metrics

🎯 Credit Scoring Logic
Factor	Weight
Past Loans Paid on Time	35%
Number of Loans Taken	25%
Loan Activity in Current Year	25%
Total Loan Volume Approved	15%

Special Conditions
If current loans > approved limit → Credit score = 0

If total EMIs > 50% of salary → Loan is rejected

🧮 Loan Approval Rules
Credit Score	Approved	Interest Rate Condition
> 50	✅ Yes	Any rate
30–50	✅ Yes	> 12%
10–30	✅ Yes	> 16%
< 10	❌ No	Rejected

🏗️ Project Structure
bash
Copy
Edit
Alemeno_assignment/
├── credit_system/          # Django settings
├── loans/                  # Business logic & APIs
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── services.py         # Scoring & eligibility logic
│   ├── tasks.py            # Celery ingestion
│   ├── tests.py
│   └── management/         # Custom commands
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── demo_api.py             # API usage script
└── test_api.py             # API tests
⚡ Quick Start
🔧 Local Setup
bash
Copy
Edit
git clone <repo-url>
cd Alemeno_assignment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
bash
Copy
Edit
python manage.py makemigrations
python manage.py migrate
python manage.py generate_sample_data --customers 5 --loans-per-customer 2
python manage.py runserver
To test the API:

bash
Copy
Edit
python demo_api.py
🐳 Docker Setup
bash
Copy
Edit
docker-compose up --build
API: http://localhost:8000

Health: http://localhost:8000/health

🧪 Testing
Run all tests:

bash
Copy
Edit
python manage.py test
Run specific tests:

bash
Copy
Edit
python manage.py test loans.tests.APITest
python manage.py test loans.tests.CreditScoreServiceTest
📈 Sample API Responses
Register Customer
json
Copy
Edit
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": 9876543210
}
Check Eligibility
json
Copy
Edit
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.5,
  "corrected_interest_rate": 12.0,
  "tenure": 24,
  "monthly_installment": 9091.13
}
Create Loan
json
Copy
Edit
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 9091.13
}
⚙️ Configuration
.env file example:

env
Copy
Edit
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@db:5432/credit_system
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
📊 Performance & Scalability
Optimized database queries

Redis caching for background jobs

Async task processing with Celery

Lightweight API with minimal DB hits

Robust error handling and validation

🔐 Security Highlights
Input validation via serializers

Accurate HTTP error responses

Safe DB operations with constraints

DRF permissions and throttling ready

🧠 Business Logic Highlights
Compound interest-based EMI calculation

Multi-factor credit scoring algorithm

Auto-correction of interest rates

Debt-to-Income (DTI) checks

Historical loan data analysis

✅ Implementation Status
Feature	Status
Django 4.x + DRF Setup	✅
PostgreSQL/SQLite Integration	✅
Customer & Loan Models	✅
All API Endpoints Implemented	✅
Credit Score Algorithm	✅
Loan Eligibility Logic	✅
Compound Interest EMI	✅
Celery + Redis Setup	✅
Excel Data Ingestion	✅
Dockerized Environment	✅
Full Test Coverage	✅
API Docs + Sample Scripts	✅
Health Check Endpoint	✅

🚀 Production Ready
✅ Local & Docker Development

✅ Full Test Suite

✅ Background Worker Integration

✅ Scaling-Ready Architecture

📞 Support
For queries or issues, refer to the codebase, tests, and demo scripts provided.
