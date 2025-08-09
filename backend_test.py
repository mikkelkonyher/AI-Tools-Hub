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

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
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

def main():
    print("🚀 Starting AI Tools Hub API Testing")
    print("=" * 50)
    
    tester = AIToolsAPITester()
    
    # Test sequence
    tests = [
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
    
    print(f"\n📋 Running {len(tests)} test suites...")
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test suite '{test_name}' failed with error: {str(e)}")
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*50}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())