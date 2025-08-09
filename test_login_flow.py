#!/usr/bin/env python3
import requests
import json

BACKEND_URL = "https://b576a147-2034-46ae-8e4d-9b11296ff056.preview.emergentagent.com"
API = f"{BACKEND_URL}/api"

def test_login():
    print("Testing login flow...")
    
    # Test login with our known user
    login_data = {
        "username": "testuser_edit123",
        "password": "Password123!"
    }
    
    response = requests.post(f"{API}/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test /me endpoint
        me_response = requests.get(f"{API}/me", headers=headers)
        print(f"Me response status: {me_response.status_code}")
        print(f"Me response: {me_response.text}")
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"✅ User authenticated: {user_info['username']}")
            return True
    
    return False

if __name__ == "__main__":
    test_login()
