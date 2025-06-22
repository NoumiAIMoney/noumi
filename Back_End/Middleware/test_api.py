#!/usr/bin/env python3
"""
Test script to demonstrate the Noumi API authentication and endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_login():
    """Test login and get token"""
    print("🔍 Testing login endpoint...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful!")
        print(f"Token: {data['token']}")
        return data['token']
    else:
        print(f"Login failed: {response.text}")
        return None


def test_authenticated_endpoint(token):
    """Test authenticated endpoint with token"""
    print("🔍 Testing /auth/me with token...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"User info: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()


def test_spending_endpoint(token):
    """Test spending endpoint with token"""
    print("🔍 Testing /spending/total with token...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/spending/total", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Spending data: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()


def main():
    """Run all tests"""
    print("🚀 Testing Noumi API...")
    print("=" * 50)
    
    # Test health (no auth required)
    test_health()
    
    # Test login and get token
    token = test_login()
    
    if token:
        # Test authenticated endpoints
        test_authenticated_endpoint(token)
        test_spending_endpoint(token)
        
        print("✅ All tests completed successfully!")
        print()
        print("💡 You can now use this token in curl commands:")
        print(f"curl -H 'Authorization: Bearer {token}' {BASE_URL}/auth/me")
    else:
        print("❌ Could not get authentication token")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://127.0.0.1:8000")
        print("Run: cd Back_End/Middleware && python start_server.py") 