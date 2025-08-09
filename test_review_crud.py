#!/usr/bin/env python3
import requests
import json

BACKEND_URL = "https://b576a147-2034-46ae-8e4d-9b11296ff056.preview.emergentagent.com"
API = f"{BACKEND_URL}/api"

def test_review_crud():
    # 1. Register a new user
    print("1. Registering user...")
    user_data = {
        "username": "testuser_edit123",
        "email": "testuser_edit123@test.com",
        "password": "Password123!"
    }
    
    response = requests.post(f"{API}/register", json=user_data)
    if response.status_code == 200:
        print(f"✅ User registered: {response.json()['username']}")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    # 2. Login
    print("2. Logging in...")
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{API}/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Logged in successfully")
    else:
        print(f"❌ Login failed: {response.text}")
        return
    
    # 3. Get current user info
    print("3. Getting user profile...")
    response = requests.get(f"{API}/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ User info: {user_info['username']} ({user_info['email']})")
    else:
        print(f"❌ Failed to get user info: {response.text}")
        return
    
    # 4. Get a tool to review
    print("4. Getting tools...")
    response = requests.get(f"{API}/tools")
    if response.status_code == 200:
        tools = response.json()["tools"]
        if tools:
            tool = tools[0]
            print(f"✅ Found tool to review: {tool['name']}")
        else:
            print("❌ No tools found")
            return
    else:
        print(f"❌ Failed to get tools: {response.text}")
        return
    
    # 5. Write a review
    print("5. Writing review...")
    review_data = {
        "tool_id": tool["id"],
        "rating": 4,
        "title": "Great tool for testing edit/delete!",
        "content": "This is a test review to check if edit and delete functionality works properly."
    }
    
    response = requests.post(f"{API}/reviews", json=review_data, headers=headers)
    if response.status_code == 200:
        review = response.json()
        print(f"✅ Review created: {review['title']} (ID: {review['id']})")
        review_id = review["id"]
    else:
        print(f"❌ Failed to create review: {response.text}")
        return
    
    # 6. Get reviews to verify
    print("6. Getting reviews...")
    response = requests.get(f"{API}/reviews/{tool['id']}")
    if response.status_code == 200:
        reviews = response.json()["reviews"]
        print(f"✅ Found {len(reviews)} reviews")
        for r in reviews:
            print(f"   - '{r['title']}' by {r['username']} (ID: {r['id']})")
    else:
        print(f"❌ Failed to get reviews: {response.text}")
    
    # 7. Edit the review
    print("7. Editing review...")
    updated_review_data = {
        "tool_id": tool["id"],
        "rating": 5,
        "title": "UPDATED: Amazing tool!",
        "content": "Updated content: This tool is even better than I initially thought!"
    }
    
    response = requests.put(f"{API}/reviews/{review_id}", json=updated_review_data, headers=headers)
    if response.status_code == 200:
        updated_review = response.json()
        print(f"✅ Review updated: {updated_review['title']}")
    else:
        print(f"❌ Failed to update review: {response.text}")
    
    # 8. Get reviews again to verify update
    print("8. Verifying update...")
    response = requests.get(f"{API}/reviews/{tool['id']}")
    if response.status_code == 200:
        reviews = response.json()["reviews"]
        for r in reviews:
            if r['id'] == review_id:
                print(f"✅ Review updated successfully: '{r['title']}' (Rating: {r['rating']}/5)")
                break
    
    print(f"\n✅ CRUD test completed! User '{user_data['username']}' can now login and see edit/delete options.")
    print(f"Frontend should show edit/delete menu for reviews by user: {user_data['username']}")

if __name__ == "__main__":
    test_review_crud()
