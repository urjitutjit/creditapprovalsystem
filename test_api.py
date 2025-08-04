#!/usr/bin/env python3
"""
Test script to demonstrate the Credit Approval System API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Testing Credit Approval System API")
    print("=" * 50)
    
    # Test 1: Register a new customer
    print("\n1. Registering a new customer...")
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": 9876543210
    }
    
    response = requests.post(f"{BASE_URL}/register", json=customer_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        customer = response.json()
        print(f"Customer created: {customer}")
        customer_id = customer['customer_id']
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 2: Check loan eligibility
    print("\n2. Checking loan eligibility...")
    eligibility_data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    
    response = requests.post(f"{BASE_URL}/check-eligibility", json=eligibility_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        eligibility = response.json()
        print(f"Eligibility result: {eligibility}")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Create a loan
    print("\n3. Creating a loan...")
    loan_data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    
    response = requests.post(f"{BASE_URL}/create-loan", json=loan_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        loan = response.json()
        print(f"Loan created: {loan}")
        loan_id = loan['loan_id']
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 4: View loan details
    print("\n4. Viewing loan details...")
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        loan_details = response.json()
        print(f"Loan details: {json.dumps(loan_details, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 5: View customer loans
    print("\n5. Viewing customer loans...")
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        customer_loans = response.json()
        print(f"Customer loans: {json.dumps(customer_loans, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 6: Health check
    print("\n6. Health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        health = response.json()
        print(f"Health status: {health}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}") 