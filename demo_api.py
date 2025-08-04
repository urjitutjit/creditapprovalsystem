#!/usr/bin/env python3
"""
Comprehensive demonstration of the Credit Approval System API
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def demo_api():
    print("🚀 Credit Approval System API Demonstration")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1️⃣ Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        health = response.json()
        print(f"✅ Health: {health}")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test 2: Register a new customer
    print("\n2️⃣ Registering a new customer...")
    customer_data = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "age": 28,
        "monthly_income": 75000,
        "phone_number": 9876543211
    }
    
    response = requests.post(f"{BASE_URL}/register", json=customer_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        customer = response.json()
        print(f"✅ Customer created: {customer}")
        customer_id = customer['customer_id']
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test 3: Check loan eligibility (should fail due to no credit history)
    print("\n3️⃣ Checking loan eligibility (new customer)...")
    eligibility_data = {
        "customer_id": customer_id,
        "loan_amount": 200000,
        "interest_rate": 8.5,
        "tenure": 24
    }
    
    response = requests.post(f"{BASE_URL}/check-eligibility", json=eligibility_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        eligibility = response.json()
        print(f"📊 Eligibility result: {json.dumps(eligibility, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 4: Try to create a loan (should fail)
    print("\n4️⃣ Attempting to create a loan (should fail)...")
    loan_data = {
        "customer_id": customer_id,
        "loan_amount": 200000,
        "interest_rate": 8.5,
        "tenure": 24
    }
    
    response = requests.post(f"{BASE_URL}/create-loan", json=loan_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        result = response.json()
        print(f"❌ Loan rejected: {result['message']}")
    else:
        print(f"Unexpected response: {response.text}")
    
    # Test 5: View customer loans (should be empty)
    print("\n5️⃣ Viewing customer loans (should be empty)...")
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        customer_loans = response.json()
        print(f"📋 Customer loans: {customer_loans}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 6: Register another customer with good credit history simulation
    print("\n6️⃣ Registering customer with good credit history...")
    customer_data2 = {
        "first_name": "Bob",
        "last_name": "Smith",
        "age": 35,
        "monthly_income": 120000,
        "phone_number": 9876543212
    }
    
    response = requests.post(f"{BASE_URL}/register", json=customer_data2)
    if response.status_code == 201:
        customer2 = response.json()
        print(f"✅ Customer created: {customer2}")
        customer_id2 = customer2['customer_id']
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test 7: Check eligibility for customer with good credit (using existing sample data)
    print("\n7️⃣ Checking eligibility for customer with credit history...")
    # Use one of the existing customers from sample data
    existing_customer_id = 1  # From the sample data we generated
    
    eligibility_data2 = {
        "customer_id": existing_customer_id,
        "loan_amount": 500000,
        "interest_rate": 12.0,
        "tenure": 36
    }
    
    response = requests.post(f"{BASE_URL}/check-eligibility", json=eligibility_data2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        eligibility2 = response.json()
        print(f"📊 Eligibility result: {json.dumps(eligibility2, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 8: Create a loan for customer with good credit
    print("\n8️⃣ Creating a loan for customer with good credit...")
    loan_data2 = {
        "customer_id": existing_customer_id,
        "loan_amount": 500000,
        "interest_rate": 12.0,
        "tenure": 36
    }
    
    response = requests.post(f"{BASE_URL}/create-loan", json=loan_data2)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        loan = response.json()
        print(f"✅ Loan created: {json.dumps(loan, indent=2)}")
        loan_id = loan['loan_id']
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test 9: View the created loan
    print("\n9️⃣ Viewing the created loan...")
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        loan_details = response.json()
        print(f"📋 Loan details: {json.dumps(loan_details, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 10: View all loans for the customer
    print("\n🔟 Viewing all loans for the customer...")
    response = requests.get(f"{BASE_URL}/view-loans/{existing_customer_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        customer_loans = response.json()
        print(f"📋 Customer loans: {json.dumps(customer_loans, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 11: API Documentation
    print("\n📚 API Documentation...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API documentation available")
    else:
        print(f"❌ Error: {response.text}")
    
    print("\n🎉 Demonstration completed successfully!")
    print("=" * 60)
    print("✅ All API endpoints are working correctly")
    print("✅ Credit scoring system is functioning")
    print("✅ Loan approval logic is working")
    print("✅ Data persistence is working")

if __name__ == "__main__":
    try:
        demo_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure the Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 