# Credit Approval System

A comprehensive Django-based credit approval system with REST API endpoints for customer registration, loan eligibility checking, and loan management.

## 🚀 Features

- **Customer Management**: Register new customers with automatic approved limit calculation
- **Credit Scoring**: Advanced credit score calculation based on historical loan data
- **Loan Eligibility**: Intelligent loan approval system with interest rate adjustments
- **Loan Management**: Create, view, and manage loans with EMI calculations
- **Background Tasks**: Celery integration for data ingestion from Excel files
- **Comprehensive Testing**: Unit tests covering all business logic and API endpoints
- **Docker Support**: Complete containerization with PostgreSQL and Redis

## 🛠 Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: SQLite (development) / PostgreSQL (production)
- **Task Queue**: Celery 5.3.4 + Redis 5.0.1
- **Data Processing**: Pandas + OpenPyXL for Excel file handling
- **Containerization**: Docker + Docker Compose
- **Testing**: Django TestCase + DRF APITestCase

## 📊 API Endpoints

### 1. Register Customer
- **POST** `/register`
- **Purpose**: Add new customer with automatic approved limit calculation
- **Formula**: `approved_limit = 36 * monthly_salary` (rounded to nearest lakh)

### 2. Check Loan Eligibility
- **POST** `/check-eligibility`
- **Purpose**: Check loan eligibility based on credit score and business rules
- **Credit Score Components**:
  - Past loans paid on time (35% weight)
  - Number of loans taken (25% weight)
  - Loan activity in current year (25% weight)
  - Loan approved volume (15% weight)

### 3. Create Loan
- **POST** `/create-loan`
- **Purpose**: Process loan application based on eligibility check

### 4. View Loan Details
- **GET** `/view-loan/{loan_id}`
- **Purpose**: Get detailed loan and customer information

### 5. View Customer Loans
- **GET** `/view-loans/{customer_id}`
- **Purpose**: Get all loans for a specific customer

### 6. Health Check
- **GET** `/health`
- **Purpose**: System health and statistics

## 🎯 Credit Scoring Logic

The system calculates credit scores (0-100) based on:

1. **Past Loans Paid on Time** (35% weight)
   - Percentage of completed loans where all EMIs were paid on time

2. **Number of Loans Taken** (25% weight)
   - 1 loan: 10 points, 2 loans: 15 points, 3 loans: 20 points, 4+: 25 points

3. **Loan Activity in Current Year** (25% weight)
   - 1 loan: 15 points, 2 loans: 20 points, 3+: 25 points

4. **Loan Approved Volume** (15% weight)
   - ≤10 lakhs: 5 points, ≤25 lakhs: 10 points, >25 lakhs: 15 points

**Special Conditions**:
- If current loans > approved limit: Credit score = 0
- If total current EMIs > 50% of monthly salary: No approval

## 📈 Loan Approval Criteria

| Credit Score | Approval | Interest Rate Requirement |
|--------------|----------|---------------------------|
| > 50        | ✅ Yes   | Any rate                  |
| 30-50       | ✅ Yes   | > 12%                     |
| 10-30       | ✅ Yes   | > 16%                     |
| < 10        | ❌ No    | No approval               |

## 🏗 Project Structure

```
Alemeno_assignment/
├── credit_system/          # Django project settings
├── loans/                  # Main application
│   ├── models.py          # Customer and Loan models
│   ├── serializers.py     # API serializers
│   ├── views.py           # API endpoints
│   ├── services.py        # Business logic (credit scoring, eligibility)
│   ├── tasks.py           # Celery background tasks
│   ├── tests.py           # Comprehensive unit tests
│   └── management/        # Django management commands
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Multi-service setup
├── .env                   # Environment variables
├── test_api.py           # API testing script
├── demo_api.py           # Comprehensive demonstration
└── README.md             # Project documentation
```

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd Alemeno_assignment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Generate Sample Data**:
   ```bash
   python manage.py generate_sample_data --customers 5 --loans-per-customer 2
   ```

4. **Start Server**:
   ```bash
   python manage.py runserver
   ```

5. **Test API**:
   ```bash
   python demo_api.py
   ```

### Docker Setup

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```

2. **Access API**:
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/health

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Tests
```bash
python manage.py test loans.tests.APITest
python manage.py test loans.tests.CreditScoreServiceTest
```

### API Testing
```bash
python demo_api.py
```

## 📊 Sample API Responses

### Register Customer
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": 9876543210
}
```

### Check Eligibility
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.5,
  "corrected_interest_rate": 12.0,
  "tenure": 24,
  "monthly_installment": 9091.13
}
```

### Create Loan
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 9091.13
}
```

## 🔧 Configuration

### Environment Variables (.env)
```
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@db:5432/credit_system
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## 📈 Performance & Scalability

- **Database**: Optimized queries with proper indexing
- **Caching**: Redis integration for session and task queue
- **Background Processing**: Celery for data ingestion tasks
- **API Performance**: Efficient serializers and minimal database queries
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes

## 🛡 Security Features

- **Input Validation**: Comprehensive serializer validation
- **Error Handling**: Proper HTTP status codes and error messages
- **Data Integrity**: Database constraints and model validation
- **API Security**: Django REST Framework security features

## 🎯 Business Logic Highlights

1. **Compound Interest EMI Calculation**: Accurate monthly installment calculation
2. **Credit Score Algorithm**: Multi-factor weighted scoring system
3. **Dynamic Interest Rate Adjustment**: Automatic rate correction based on credit score
4. **Debt-to-Income Ratio Check**: Prevents over-leveraging
5. **Historical Data Analysis**: Comprehensive loan history evaluation

## ✅ Implementation Status

- ✅ Django 4+ with DRF setup
- ✅ PostgreSQL/SQLite database integration
- ✅ Customer and Loan models
- ✅ All required API endpoints
- ✅ Credit scoring algorithm
- ✅ Loan eligibility logic
- ✅ EMI calculation with compound interest
- ✅ Background task setup (Celery + Redis)
- ✅ Comprehensive unit tests
- ✅ Docker containerization
- ✅ Data ingestion from Excel files
- ✅ Error handling and validation
- ✅ API documentation
- ✅ Sample data generation
- ✅ Health check endpoint

## 🚀 Ready for Production

The system is fully functional and ready for:
- **Development**: Local development with SQLite
- **Testing**: Comprehensive test suite
- **Production**: Docker deployment with PostgreSQL
- **Scaling**: Background task processing with Celery

## 📞 Support

For questions or issues, please refer to the comprehensive test suite and API documentation included in the project. #   c r e d i t a p p r o v a l s y s t e m _ a s s i g n m e n t  
 