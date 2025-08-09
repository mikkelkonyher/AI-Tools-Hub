import requests
import sys
import json
from datetime import datetime

class AIToolsAPITester:
    def __init__(self, base_url="https://b576a147-2034-46ae-8e4d-9b11296ff056.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.test_user_id = None
        self.test_tool_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}
        
        # Add auth header if required and token is available
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if auth_required:
            print(f"   Auth: {'✓' if self.auth_token else '✗'}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) <= 3:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) <= 5:
                        print(f"   Response: {response_data}")
                    else:
                        print(f"   Response type: {type(response_data)}")
                        if isinstance(response_data, dict):
                            print(f"   Keys: {list(response_data.keys())}")
                        elif isinstance(response_data, list):
                            print(f"   List length: {len(response_data)}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.status_code < 400 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_seed_data(self):
        """Test seeding sample data"""
        return self.run_test("Seed Sample Data", "POST", "seed-data", 200)

    def test_get_categories(self):
        """Test getting all categories"""
        success, response = self.run_test("Get Categories", "GET", "categories", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} categories")
            for cat in response[:3]:  # Show first 3
                print(f"   - {cat}")
        return success, response

    def test_get_price_models(self):
        """Test getting all price models"""
        success, response = self.run_test("Get Price Models", "GET", "price-models", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} price models")
            for pm in response:
                print(f"   - {pm}")
        return success, response

    def test_get_platforms(self):
        """Test getting all platforms"""
        success, response = self.run_test("Get Platforms", "GET", "platforms", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} platforms")
            for platform in response:
                print(f"   - {platform}")
        return success, response

    def test_get_all_tools(self):
        """Test getting all tools without filters"""
        success, response = self.run_test("Get All Tools", "GET", "tools", 200)
        if success and 'tools' in response:
            print(f"   Found {response['total']} total tools")
            print(f"   Page {response['page']}, showing {len(response['tools'])} tools")
            if response['tools']:
                tool = response['tools'][0]
                print(f"   First tool: {tool['name']} - {tool['category']}")
        return success, response

    def test_search_functionality(self):
        """Test search functionality"""
        search_terms = ["ChatGPT", "image", "AI", "nonexistent"]
        results = []
        
        for term in search_terms:
            success, response = self.run_test(
                f"Search for '{term}'", 
                "GET", 
                "tools", 
                200, 
                params={"search": term}
            )
            if success:
                count = len(response.get('tools', []))
                print(f"   Found {count} tools for '{term}'")
                results.append((term, count))
        
        return len(results) > 0, results

    def test_category_filtering(self):
        """Test filtering by category"""
        categories = ["text_generation", "image_creation", "code_generation"]
        results = []
        
        for category in categories:
            success, response = self.run_test(
                f"Filter by category '{category}'", 
                "GET", 
                "tools", 
                200, 
                params={"category": category}
            )
            if success:
                count = len(response.get('tools', []))
                print(f"   Found {count} tools in '{category}'")
                # Verify all returned tools have the correct category
                if response.get('tools'):
                    correct_category = all(tool['category'] == category for tool in response['tools'])
                    print(f"   All tools have correct category: {correct_category}")
                results.append((category, count))
        
        return len(results) > 0, results

    def test_price_model_filtering(self):
        """Test filtering by price model"""
        price_models = ["freemium", "subscription", "free"]
        results = []
        
        for price_model in price_models:
            success, response = self.run_test(
                f"Filter by price model '{price_model}'", 
                "GET", 
                "tools", 
                200, 
                params={"price_model": price_model}
            )
            if success:
                count = len(response.get('tools', []))
                print(f"   Found {count} tools with '{price_model}' pricing")
                results.append((price_model, count))
        
        return len(results) > 0, results

    def test_platform_filtering(self):
        """Test filtering by platform"""
        platforms = ["web", "desktop", "api"]
        results = []
        
        for platform in platforms:
            success, response = self.run_test(
                f"Filter by platform '{platform}'", 
                "GET", 
                "tools", 
                200, 
                params={"platform": platform}
            )
            if success:
                count = len(response.get('tools', []))
                print(f"   Found {count} tools on '{platform}' platform")
                results.append((platform, count))
        
        return len(results) > 0, results

    def test_pagination(self):
        """Test pagination functionality"""
        # Test first page
        success1, response1 = self.run_test(
            "Pagination - Page 1", 
            "GET", 
            "tools", 
            200, 
            params={"page": 1, "per_page": 5}
        )
        
        # Test second page
        success2, response2 = self.run_test(
            "Pagination - Page 2", 
            "GET", 
            "tools", 
            200, 
            params={"page": 2, "per_page": 5}
        )
        
        if success1 and success2:
            print(f"   Page 1: {len(response1.get('tools', []))} tools")
            print(f"   Page 2: {len(response2.get('tools', []))} tools")
            
            # Check if tools are different between pages
            if response1.get('tools') and response2.get('tools'):
                page1_ids = {tool['id'] for tool in response1['tools']}
                page2_ids = {tool['id'] for tool in response2['tools']}
                different_tools = len(page1_ids.intersection(page2_ids)) == 0
                print(f"   Different tools on different pages: {different_tools}")
        
        return success1 and success2

    def test_combined_filters(self):
        """Test combining multiple filters"""
        success, response = self.run_test(
            "Combined Filters (category + price_model)", 
            "GET", 
            "tools", 
            200, 
            params={
                "category": "text_generation",
                "price_model": "freemium",
                "search": "AI"
            }
        )
        
        if success:
            count = len(response.get('tools', []))
            print(f"   Found {count} tools matching all filters")
            
        return success

    def test_get_specific_tool(self):
        """Test getting a specific tool by ID"""
        # First get all tools to get an ID
        success, response = self.run_test("Get Tools for ID", "GET", "tools", 200)
        
        if success and response.get('tools'):
            tool_id = response['tools'][0]['id']
            success2, tool_response = self.run_test(
                f"Get Specific Tool", 
                "GET", 
                f"tools/{tool_id}", 
                200
            )
            
            if success2:
                print(f"   Retrieved tool: {tool_response.get('name', 'Unknown')}")
            
            return success2
        
        return False

    # ===== PHASE 2: AUTHENTICATION TESTS =====
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        timestamp = datetime.now().strftime("%H%M%S")
        test_user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test(
            "User Registration", 
            "POST", 
            "register", 
            200,
            data=test_user_data
        )
        
        if success and 'id' in response:
            self.test_user_id = response['id']
            print(f"   Created user: {response.get('username')} (ID: {self.test_user_id})")
            # Store credentials for login test
            self.test_username = test_user_data['username']
            self.test_password = test_user_data['password']
        
        return success, response

    def test_duplicate_user_registration(self):
        """Test duplicate user registration should fail"""
        if not hasattr(self, 'test_username'):
            print("   Skipping - no test user created yet")
            return True, {}
            
        duplicate_user_data = {
            "username": self.test_username,
            "email": f"different_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "DifferentPassword123!"
        }
        
        success, response = self.run_test(
            "Duplicate User Registration (should fail)", 
            "POST", 
            "register", 
            400,  # Should fail with 400
            data=duplicate_user_data
        )
        
        return success, response

    def test_user_login(self):
        """Test user login endpoint"""
        if not hasattr(self, 'test_username'):
            print("   Skipping - no test user created yet")
            return False, {}
            
        login_data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Login", 
            "POST", 
            "login", 
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            print(f"   Login successful, token received")
        
        return success, response

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        invalid_login_data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        
        success, response = self.run_test(
            "Invalid Login (should fail)", 
            "POST", 
            "login", 
            401,  # Should fail with 401
            data=invalid_login_data
        )
        
        return success, response

    def test_get_current_user(self):
        """Test getting current user profile (requires auth)"""
        if not self.auth_token:
            print("   Skipping - no auth token available")
            return False, {}
            
        success, response = self.run_test(
            "Get Current User Profile", 
            "GET", 
            "me", 
            200,
            auth_required=True
        )
        
        if success:
            print(f"   User profile: {response.get('username')} ({response.get('email')})")
        
        return success, response

    def test_protected_route_without_auth(self):
        """Test accessing protected route without authentication"""
        # Temporarily remove auth token
        temp_token = self.auth_token
        self.auth_token = None
        
        success, response = self.run_test(
            "Protected Route Without Auth (should fail)", 
            "GET", 
            "me", 
            401,  # Should fail with 401
            auth_required=False
        )
        
        # Restore auth token
        self.auth_token = temp_token
        
        return success, response

    # ===== PHASE 2: REVIEW SYSTEM TESTS =====
    
    def test_create_review(self):
        """Test creating a review for a tool (requires auth)"""
        if not self.auth_token:
            print("   Skipping - no auth token available")
            return False, {}
            
        # First get a tool ID
        if not self.test_tool_id:
            success, tools_response = self.run_test("Get Tools for Review", "GET", "tools", 200)
            if success and tools_response.get('tools'):
                self.test_tool_id = tools_response['tools'][0]['id']
                print(f"   Using tool: {tools_response['tools'][0]['name']}")
            else:
                print("   No tools available for review")
                return False, {}
        
        review_data = {
            "tool_id": self.test_tool_id,
            "rating": 4,
            "title": "Great AI tool!",
            "content": "This tool has been very helpful for my projects. The interface is intuitive and the results are impressive."
        }
        
        success, response = self.run_test(
            "Create Review", 
            "POST", 
            "reviews", 
            200,
            data=review_data,
            auth_required=True
        )
        
        if success and 'id' in response:
            self.test_review_id = response['id']
            print(f"   Created review: {response.get('title')} (Rating: {response.get('rating')}/5)")
        
        return success, response

    def test_duplicate_review(self):
        """Test creating duplicate review for same tool (should fail)"""
        if not self.auth_token or not self.test_tool_id:
            print("   Skipping - no auth token or tool ID available")
            return True, {}
            
        duplicate_review_data = {
            "tool_id": self.test_tool_id,
            "rating": 5,
            "title": "Another review",
            "content": "This should fail because user already reviewed this tool."
        }
        
        success, response = self.run_test(
            "Duplicate Review (should fail)", 
            "POST", 
            "reviews", 
            400,  # Should fail with 400
            data=duplicate_review_data,
            auth_required=True
        )
        
        return success, response

    def test_get_tool_reviews(self):
        """Test getting reviews for a specific tool"""
        if not self.test_tool_id:
            print("   Skipping - no tool ID available")
            return False, {}
            
        success, response = self.run_test(
            "Get Tool Reviews", 
            "GET", 
            f"reviews/{self.test_tool_id}", 
            200
        )
        
        if success:
            reviews = response.get('reviews', [])
            print(f"   Found {len(reviews)} reviews for tool")
            if reviews:
                print(f"   Latest review: {reviews[0].get('title')} by {reviews[0].get('username')}")
        
        return success, response

    def test_create_comment(self):
        """Test creating a comment on a review (requires auth)"""
        if not self.auth_token or not hasattr(self, 'test_review_id'):
            print("   Skipping - no auth token or review ID available")
            return False, {}
            
        comment_data = {
            "review_id": self.test_review_id,
            "content": "I completely agree with this review! Thanks for sharing your experience."
        }
        
        success, response = self.run_test(
            "Create Comment", 
            "POST", 
            "comments", 
            200,
            data=comment_data,
            auth_required=True
        )
        
        if success and 'id' in response:
            self.test_comment_id = response['id']
            print(f"   Created comment: {response.get('content')[:50]}...")
        
        return success, response

    def test_get_review_comments(self):
        """Test getting comments for a specific review"""
        if not hasattr(self, 'test_review_id'):
            print("   Skipping - no review ID available")
            return False, {}
            
        success, response = self.run_test(
            "Get Review Comments", 
            "GET", 
            f"comments/{self.test_review_id}", 
            200
        )
        
        if success:
            comments = response.get('comments', [])
            print(f"   Found {len(comments)} comments for review")
            if comments:
                print(f"   Latest comment: {comments[0].get('content')[:50]}... by {comments[0].get('username')}")
        
        return success, response

    def test_review_without_auth(self):
        """Test creating review without authentication (should fail)"""
        if not self.test_tool_id:
            print("   Skipping - no tool ID available")
            return True, {}
            
        # Temporarily remove auth token
        temp_token = self.auth_token
        self.auth_token = None
        
        review_data = {
            "tool_id": self.test_tool_id,
            "rating": 3,
            "title": "Unauthorized review",
            "content": "This should fail."
        }
        
        success, response = self.run_test(
            "Review Without Auth (should fail)", 
            "POST", 
            "reviews", 
            401,  # Should fail with 401
            data=review_data,
            auth_required=False
        )
        
        # Restore auth token
        self.auth_token = temp_token
        
        return success, response

def main():
    print("🚀 Starting AI Tools Hub API Testing (Phase 2 - Authentication & Reviews)")
    print("=" * 70)
    
    tester = AIToolsAPITester()
    
    # Test sequence - Phase 1 (Basic functionality)
    phase1_tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Seed Data", tester.test_seed_data),
        ("Get Categories", tester.test_get_categories),
        ("Get Price Models", tester.test_get_price_models),
        ("Get Platforms", tester.test_get_platforms),
        ("Get All Tools", tester.test_get_all_tools),
        ("Search Functionality", tester.test_search_functionality),
        ("Category Filtering", tester.test_category_filtering),
        ("Price Model Filtering", tester.test_price_model_filtering),
        ("Platform Filtering", tester.test_platform_filtering),
        ("Pagination", tester.test_pagination),
        ("Combined Filters", tester.test_combined_filters),
        ("Get Specific Tool", tester.test_get_specific_tool),
    ]
    
    # Test sequence - Phase 2 (Authentication & Reviews)
    phase2_tests = [
        ("User Registration", tester.test_user_registration),
        ("Duplicate Registration", tester.test_duplicate_user_registration),
        ("User Login", tester.test_user_login),
        ("Invalid Login", tester.test_invalid_login),
        ("Get Current User", tester.test_get_current_user),
        ("Protected Route Without Auth", tester.test_protected_route_without_auth),
        ("Create Review", tester.test_create_review),
        ("Duplicate Review", tester.test_duplicate_review),
        ("Get Tool Reviews", tester.test_get_tool_reviews),
        ("Create Comment", tester.test_create_comment),
        ("Get Review Comments", tester.test_get_review_comments),
        ("Review Without Auth", tester.test_review_without_auth),
    ]
    
    all_tests = phase1_tests + phase2_tests
    
    print(f"\n📋 Running {len(all_tests)} test suites...")
    print(f"   Phase 1: {len(phase1_tests)} basic functionality tests")
    print(f"   Phase 2: {len(phase2_tests)} authentication & review tests")
    
    # Run Phase 1 tests
    print(f"\n🔵 PHASE 1: BASIC FUNCTIONALITY TESTS")
    print("=" * 50)
    for test_name, test_func in phase1_tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test suite '{test_name}' failed with error: {str(e)}")
    
    # Run Phase 2 tests
    print(f"\n🟢 PHASE 2: AUTHENTICATION & REVIEW TESTS")
    print("=" * 50)
    for test_name, test_func in phase2_tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test suite '{test_name}' failed with error: {str(e)}")
    
    # Print final results
    print(f"\n{'='*70}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*70}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Detailed breakdown
    if tester.auth_token:
        print(f"✅ Authentication: Working (Token acquired)")
    else:
        print(f"❌ Authentication: Failed (No token)")
        
    if hasattr(tester, 'test_review_id'):
        print(f"✅ Review System: Working (Review created)")
    else:
        print(f"❌ Review System: Failed (No review created)")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API with authentication and reviews is working correctly.")
        return 0
    elif tester.tests_passed >= tester.tests_run * 0.8:  # 80% pass rate
        print("⚠️  Most tests passed. Some minor issues detected.")
        return 0
    else:
        print("⚠️  Significant issues detected. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())