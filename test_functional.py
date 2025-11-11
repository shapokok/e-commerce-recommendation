"""
Functional Testing Suite for E-Commerce Recommendation System
Tests all main functionality including registration, authentication, products, and recommendations
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple

API_URL = "http://localhost:8000"

class Color:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    """Store test result information"""
    def __init__(self, test_num: int, function: str, input_data: str, 
                 expected: str, actual: str, status: str):
        self.test_num = test_num
        self.function = function
        self.input_data = input_data
        self.expected = expected
        self.actual = actual
        self.status = status

class FunctionalTester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.test_counter = 1
        self.passed = 0
        self.failed = 0
        
    def print_header(self, title: str):
        """Print formatted test section header"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}  {title}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}\n")
    
    def run_test(self, function: str, input_data: Dict, 
                 expected_status: int, expected_keys: List[str] = None) -> TestResult:
        """Execute a test case and record results"""
        test_num = self.test_counter
        self.test_counter += 1
        
        try:
            # Determine HTTP method and endpoint
            if "register" in function.lower():
                response = requests.post(f"{API_URL}/api/register", json=input_data)
            elif "login" in function.lower():
                response = requests.post(f"{API_URL}/api/login", json=input_data)
            elif "product" in function.lower() and "create" in function.lower():
                response = requests.post(f"{API_URL}/api/products", json=input_data)
            elif "interaction" in function.lower():
                response = requests.post(f"{API_URL}/api/interactions", json=input_data)
            elif "recommendation" in function.lower():
                user_id = input_data.get('user_id', '')
                response = requests.get(f"{API_URL}/api/recommendations/{user_id}?n=10")
            elif "search" in function.lower():
                search_term = input_data.get('search', '')
                response = requests.get(f"{API_URL}/api/products?search={search_term}")
            elif "category" in function.lower() and "filter" in function.lower():
                category = input_data.get('category', '')
                response = requests.get(f"{API_URL}/api/products?category={category}")
            elif "profile" in function.lower() and "update" in function.lower():
                user_id = input_data.get('user_id', '')
                update_data = {k: v for k, v in input_data.items() if k != 'user_id'}
                response = requests.put(f"{API_URL}/api/users/{user_id}", json=update_data)
            elif "history" in function.lower():
                user_id = input_data.get('user_id', '')
                response = requests.get(f"{API_URL}/api/users/{user_id}/history")
            else:
                response = requests.get(f"{API_URL}/api/products")
            
            # Check response
            status_match = response.status_code == expected_status
            
            if response.status_code in [200, 201]:
                data = response.json()
                keys_match = True
                if expected_keys:
                    keys_match = all(key in data for key in expected_keys)
                
                if status_match and keys_match:
                    status = "PASSED"
                    self.passed += 1
                    expected = f"Status {expected_status}, keys: {expected_keys}"
                    actual = f"Status {response.status_code}, response received"
                else:
                    status = "FAILED"
                    self.failed += 1
                    expected = f"Status {expected_status}, keys: {expected_keys}"
                    actual = f"Status {response.status_code}, missing keys"
            else:
                if status_match:
                    status = "PASSED"
                    self.passed += 1
                    expected = f"Status {expected_status} (error expected)"
                    actual = f"Status {response.status_code}"
                else:
                    status = "FAILED"
                    self.failed += 1
                    expected = f"Status {expected_status}"
                    actual = f"Status {response.status_code}"
            
            # Create result
            result = TestResult(
                test_num=test_num,
                function=function,
                input_data=json.dumps(input_data, indent=2),
                expected=expected,
                actual=actual,
                status=status
            )
            
            # Print result
            color = Color.GREEN if status == "PASSED" else Color.RED
            print(f"{color}Test #{test_num}: {function} - {status}{Color.END}")
            print(f"  Input: {json.dumps(input_data)}")
            print(f"  Expected: {expected}")
            print(f"  Actual: {actual}\n")
            
        except Exception as e:
            status = "FAILED"
            self.failed += 1
            result = TestResult(
                test_num=test_num,
                function=function,
                input_data=json.dumps(input_data, indent=2),
                expected=f"Status {expected_status}",
                actual=f"Exception: {str(e)}",
                status=status
            )
            print(f"{Color.RED}Test #{test_num}: {function} - FAILED{Color.END}")
            print(f"  Exception: {str(e)}\n")
        
        self.results.append(result)
        return result
    
    def test_registration(self):
        """Test user registration functionality"""
        self.print_header("USER REGISTRATION TESTS")
        
        # Test 1: Valid registration
        self.run_test(
            "User Registration (Valid)",
            {
                "username": f"test_user_{datetime.now().timestamp()}",
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "password": "password123",
                "preferences": ["Electronics", "Books"]
            },
            200,
            ["message", "user_id", "username"]
        )
        
        # Test 2: Duplicate email
        self.run_test(
            "User Registration (Duplicate Email)",
            {
                "username": "duplicate_user",
                "email": "alice@example.com",  # Existing email
                "password": "password123"
            },
            400  # Should fail
        )
        
        # Test 3: Invalid email format
        self.run_test(
            "User Registration (Invalid Email)",
            {
                "username": "invalid_email_user",
                "email": "not-an-email",
                "password": "password123"
            },
            422  # Validation error
        )
    
    def test_authentication(self):
        """Test user login functionality"""
        self.print_header("USER AUTHENTICATION TESTS")
        
        # Test 4: Valid login
        self.run_test(
            "User Login (Valid)",
            {
                "email": "alice@example.com",
                "password": "password123"
            },
            200,
            ["message", "user_id", "username"]
        )
        
        # Test 5: Invalid password
        self.run_test(
            "User Login (Invalid Password)",
            {
                "email": "alice@example.com",
                "password": "wrongpassword"
            },
            401  # Unauthorized
        )
        
        # Test 6: Non-existent user
        self.run_test(
            "User Login (Non-existent User)",
            {
                "email": "nonexistent@example.com",
                "password": "password123"
            },
            401  # Unauthorized
        )
    
    def test_products(self):
        """Test product management functionality"""
        self.print_header("PRODUCT MANAGEMENT TESTS")
        
        # Test 7: Get all products
        self.run_test(
            "Get All Products",
            {},
            200,
            ["products", "count"]
        )
        
        # Test 8: Search products
        self.run_test(
            "Search Products (Laptop)",
            {"search": "laptop"},
            200,
            ["products", "count"]
        )
        
        # Test 9: Filter by category
        self.run_test(
            "Filter Products by Category (Electronics)",
            {"category": "Electronics"},
            200,
            ["products", "count"]
        )
        
        # Test 10: Create product
        self.run_test(
            "Create Product",
            {
                "name": f"Test Product {datetime.now().timestamp()}",
                "description": "Test product for functional testing",
                "category": "Electronics",
                "price": 99.99,
                "image_url": "https://via.placeholder.com/300"
            },
            200,
            ["message", "product_id"]
        )
    
    def test_interactions(self):
        """Test user interaction tracking"""
        self.print_header("INTERACTION TRACKING TESTS")
        
        # Get a valid user ID
        login_response = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"}
        )
        
        if login_response.status_code == 200:
            user_id = login_response.json()["user_id"]
            
            # Get a product ID
            products_response = requests.get(f"{API_URL}/api/products")
            if products_response.status_code == 200:
                products = products_response.json()["products"]
                if products:
                    product_id = products[0]["_id"]
                    
                    # Test 11: Track view
                    self.run_test(
                        "Track Interaction (View)",
                        {
                            "user_id": user_id,
                            "product_id": product_id,
                            "interaction_type": "view"
                        },
                        200,
                        ["message", "interaction_id"]
                    )
                    
                    # Test 12: Track like
                    self.run_test(
                        "Track Interaction (Like)",
                        {
                            "user_id": user_id,
                            "product_id": product_id,
                            "interaction_type": "like"
                        },
                        200,
                        ["message", "interaction_id"]
                    )
                    
                    # Test 13: Track rating
                    self.run_test(
                        "Track Interaction (Rating)",
                        {
                            "user_id": user_id,
                            "product_id": product_id,
                            "interaction_type": "rating",
                            "rating": 5
                        },
                        200,
                        ["message", "interaction_id"]
                    )
    
    def test_recommendations(self):
        """Test recommendation system"""
        self.print_header("RECOMMENDATION SYSTEM TESTS")
        
        # Get a valid user ID
        login_response = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"}
        )
        
        if login_response.status_code == 200:
            user_id = login_response.json()["user_id"]
            
            # Test 14: Get recommendations
            self.run_test(
                "Get User Recommendations",
                {"user_id": user_id},
                200,
                ["user_id", "recommendations", "count"]
            )
    
    def test_profile(self):
        """Test user profile functionality"""
        self.print_header("USER PROFILE TESTS")
        
        # Get a valid user ID
        login_response = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"}
        )
        
        if login_response.status_code == 200:
            user_id = login_response.json()["user_id"]
            
            # Test 15: Update profile
            self.run_test(
                "Update User Profile",
                {
                    "user_id": user_id,
                    "username": f"alice_updated_{datetime.now().timestamp()}",
                    "preferences": ["Electronics", "Books", "Sports"]
                },
                200,
                ["message", "user"]
            )
            
            # Test 16: Get user history
            self.run_test(
                "Get User History",
                {"user_id": user_id},
                200,
                ["user_id", "history", "count"]
            )
    
    def generate_summary(self):
        """Generate test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{Color.GREEN}Passed: {self.passed}{Color.END}")
        print(f"{Color.RED}Failed: {self.failed}{Color.END}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        if self.failed > 0:
            print(f"{Color.YELLOW}Failed Tests:{Color.END}")
            for result in self.results:
                if result.status == "FAILED":
                    print(f"  - Test #{result.test_num}: {result.function}")
    
    def save_results(self, filename: str = "functional_test_results.json"):
        """Save test results to JSON file"""
        results_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(self.results),
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": (self.passed / len(self.results) * 100) if self.results else 0,
            "tests": [
                {
                    "test_num": r.test_num,
                    "function": r.function,
                    "input_data": r.input_data,
                    "expected": r.expected,
                    "actual": r.actual,
                    "status": r.status
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n{Color.GREEN}Results saved to {filename}{Color.END}")

def main():
    """Run all functional tests"""
    print(f"{Color.BOLD}{Color.BLUE}")
    print("="*70)
    print("  E-COMMERCE RECOMMENDATION SYSTEM - FUNCTIONAL TESTING")
    print("="*70)
    print(f"{Color.END}")
    print(f"API Endpoint: {API_URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tester = FunctionalTester()
    
    # Run all test suites
    tester.test_registration()
    tester.test_authentication()
    tester.test_products()
    tester.test_interactions()
    tester.test_recommendations()
    tester.test_profile()
    
    # Generate summary
    tester.generate_summary()
    
    # Save results
    tester.save_results()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Testing interrupted by user{Color.END}")
    except Exception as e:
        print(f"\n{Color.RED}Error during testing: {e}{Color.END}")
        import traceback
        traceback.print_exc()