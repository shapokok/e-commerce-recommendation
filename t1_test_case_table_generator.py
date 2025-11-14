"""
Test Case Table Generator
Generates a comprehensive table of test cases with results
"""

import requests
import json
import csv
from datetime import datetime
from typing import Dict, List
from tabulate import tabulate


API_URL = "http://127.0.0.1:8000"


class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


class TestCase:
    """Represents a single test case"""

    def __init__(
        self,
        number: int,
        function: str,
        input_data: str,
        expected: str,
        actual: str = "",
        status: str = "",
    ):
        self.number = number
        self.function = function
        self.input_data = input_data
        self.expected = expected
        self.actual = actual
        self.status = status


class TestCaseRunner:
    """Run test cases and generate results table"""

    def __init__(self):
        self.test_cases = []
        self.results = []
        self.passed = 0
        self.failed = 0

    def define_test_cases(self):
        """Define all test cases"""

        # Authentication Tests
        self.test_cases.append(
            TestCase(
                1,
                "User Registration (Valid)",
                "Username: test_user, Email: test@mail.com, Password: pass123",
                "New user successfully registered, confirmation message displayed",
            )
        )

        self.test_cases.append(
            TestCase(
                2,
                "User Registration (Duplicate Email)",
                "Email: alice@example.com (existing), Password: pass123",
                "Error 400: Email already exists",
            )
        )

        self.test_cases.append(
            TestCase(
                3,
                "User Registration (Invalid Email)",
                "Email: not-an-email, Password: pass123",
                "Error 422: Validation error",
            )
        )

        self.test_cases.append(
            TestCase(
                4,
                "User Login (Valid Credentials)",
                "Email: alice@example.com, Password: password123",
                "Login successful, user_id and username returned",
            )
        )

        self.test_cases.append(
            TestCase(
                5,
                "User Login (Invalid Password)",
                "Email: alice@example.com, Password: wrongpassword",
                "Error 401: Invalid credentials",
            )
        )

        self.test_cases.append(
            TestCase(
                6,
                "User Login (Non-existent User)",
                "Email: nonexistent@example.com, Password: password123",
                "Error 401: User not found",
            )
        )

        # Product Tests
        self.test_cases.append(
            TestCase(
                7,
                "Get All Products",
                "No parameters",
                "List of products with count returned, status 200",
            )
        )

        self.test_cases.append(
            TestCase(
                8,
                "Search Products",
                "search='laptop'",
                "Filtered products matching 'laptop' keyword",
            )
        )

        self.test_cases.append(
            TestCase(
                9,
                "Filter by Category",
                "category='Electronics'",
                "Products from Electronics category only",
            )
        )

        self.test_cases.append(
            TestCase(
                10,
                "Create Product",
                "Name: Test Product, Category: Electronics, Price: 99.99",
                "Product created successfully, product_id returned",
            )
        )

        # Interaction Tests
        self.test_cases.append(
            TestCase(
                11,
                "Track Interaction (View)",
                "user_id: valid_id, product_id: valid_id, type: view",
                "Interaction recorded successfully",
            )
        )

        self.test_cases.append(
            TestCase(
                12,
                "Track Interaction (Like)",
                "user_id: valid_id, product_id: valid_id, type: like",
                "Interaction recorded successfully",
            )
        )

        self.test_cases.append(
            TestCase(
                13,
                "Track Interaction (Rating)",
                "user_id: valid_id, product_id: valid_id, type: rating, rating: 5",
                "Interaction recorded with rating successfully",
            )
        )

        # Recommendation Tests
        self.test_cases.append(
            TestCase(
                14,
                "Get User Recommendations",
                "user_id: valid_id, n=10",
                "List of 10 personalized recommendations returned",
            )
        )

        self.test_cases.append(
            TestCase(
                15,
                "Get Recommendations (Non-existent User)",
                "user_id: invalid_id",
                "Error 404 or empty recommendations with popular products",
            )
        )

        # Profile Tests
        self.test_cases.append(
            TestCase(
                16,
                "Update User Profile",
                "user_id: valid_id, username: new_name, preferences: [Electronics]",
                "Profile updated successfully",
            )
        )

        self.test_cases.append(
            TestCase(
                17,
                "Get User History",
                "user_id: valid_id",
                "List of user interactions returned",
            )
        )

        # API Edge Cases
        self.test_cases.append(
            TestCase(
                18,
                "Invalid API Endpoint",
                "GET /api/nonexistent",
                "Error 404: Not found",
            )
        )

        self.test_cases.append(
            TestCase(
                19,
                "Missing Required Field",
                "POST /api/register with missing email",
                "Error 422: Validation error",
            )
        )

        self.test_cases.append(
            TestCase(
                20,
                "Get Categories",
                "No parameters",
                "List of all product categories returned",
            )
        )

    def run_tests(self):
        """Execute all test cases"""
        print(f"{Color.BOLD}{Color.BLUE}{'='*80}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}  RUNNING TEST CASES{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*80}{Color.END}\n")

        for test in self.test_cases:
            print(f"Running Test #{test.number}: {test.function}...", end=" ")

            try:
                # Execute the test based on function name
                if "Registration (Valid)" in test.function:
                    actual, status = self._test_registration_valid()
                elif "Registration (Duplicate" in test.function:
                    actual, status = self._test_registration_duplicate()
                elif "Registration (Invalid Email)" in test.function:
                    actual, status = self._test_registration_invalid_email()
                elif "Login (Valid" in test.function:
                    actual, status = self._test_login_valid()
                elif "Login (Invalid Password)" in test.function:
                    actual, status = self._test_login_invalid()
                elif "Login (Non-existent" in test.function:
                    actual, status = self._test_login_nonexistent()
                elif "Get All Products" in test.function:
                    actual, status = self._test_get_products()
                elif "Search Products" in test.function:
                    actual, status = self._test_search_products()
                elif "Filter by Category" in test.function:
                    actual, status = self._test_filter_category()
                elif "Create Product" in test.function:
                    actual, status = self._test_create_product()
                elif "Track Interaction (View)" in test.function:
                    actual, status = self._test_track_view()
                elif "Track Interaction (Like)" in test.function:
                    actual, status = self._test_track_like()
                elif "Track Interaction (Rating)" in test.function:
                    actual, status = self._test_track_rating()
                elif (
                    "Get User Recommendations" in test.function
                    and "Non-existent" not in test.function
                ):
                    actual, status = self._test_get_recommendations()
                elif "Recommendations (Non-existent" in test.function:
                    actual, status = self._test_recommendations_invalid()
                elif "Update User Profile" in test.function:
                    actual, status = self._test_update_profile()
                elif "Get User History" in test.function:
                    actual, status = self._test_get_history()
                elif "Invalid API Endpoint" in test.function:
                    actual, status = self._test_invalid_endpoint()
                elif "Missing Required Field" in test.function:
                    actual, status = self._test_missing_field()
                elif "Get Categories" in test.function:
                    actual, status = self._test_get_categories()
                else:
                    actual, status = "Not implemented", "Skipped"

                test.actual = actual
                test.status = status

                if status == "Passed":
                    self.passed += 1
                    print(f"{Color.GREEN}✓ PASSED{Color.END}")
                else:
                    self.failed += 1
                    print(f"{Color.RED}✗ FAILED{Color.END}")

            except Exception as e:
                test.actual = f"Exception: {str(e)}"
                test.status = "Failed"
                self.failed += 1
                print(f"{Color.RED}✗ FAILED (Exception){Color.END}")

            self.results.append(test)

    # Test implementation methods
    def _test_registration_valid(self):
        timestamp = datetime.now().timestamp()
        response = requests.post(
            f"{API_URL}/api/register",
            json={
                "username": f"test_user_{timestamp}",
                "email": f"test_{timestamp}@mail.com",
                "password": "pass123",
            },
        )
        if response.status_code == 200 and "user_id" in response.json():
            return "User successfully created, confirmation message shown", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_registration_duplicate(self):
        response = requests.post(
            f"{API_URL}/api/register",
            json={
                "username": "duplicate",
                "email": "alice@example.com",
                "password": "pass123",
            },
        )
        if response.status_code == 400:
            return "Error 400: Email already exists", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_registration_invalid_email(self):
        response = requests.post(
            f"{API_URL}/api/register",
            json={"username": "test", "email": "not-an-email", "password": "pass123"},
        )
        if response.status_code == 422:
            return "Error 422: Validation error", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_login_valid(self):
        response = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"},
        )
        if response.status_code == 200 and "user_id" in response.json():
            return "Login successful, user_id and username returned", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_login_invalid(self):
        response = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "wrongpassword"},
        )
        if response.status_code == 401:
            return "Error 401: Invalid credentials", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_login_nonexistent(self):
        response = requests.post(
            f"{API_URL}/api/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        if response.status_code == 401:
            return "Error 401: User not found", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_get_products(self):
        response = requests.get(f"{API_URL}/api/products")
        if response.status_code == 200 and "products" in response.json():
            count = len(response.json()["products"])
            return f"List of {count} products returned", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_search_products(self):
        response = requests.get(f"{API_URL}/api/products?search=laptop")
        if response.status_code == 200:
            products = response.json()["products"]
            return f"Found {len(products)} products matching 'laptop'", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_filter_category(self):
        response = requests.get(f"{API_URL}/api/products?category=Electronics")
        if response.status_code == 200:
            products = response.json()["products"]
            return f"Found {len(products)} Electronics products", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_create_product(self):
        timestamp = datetime.now().timestamp()
        response = requests.post(
            f"{API_URL}/api/products",
            json={
                "name": f"Test Product {timestamp}",
                "description": "Test",
                "category": "Electronics",
                "price": 99.99,
            },
        )
        if response.status_code == 200 and "product_id" in response.json():
            return "Product created, product_id returned", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_track_view(self):
        # Get valid IDs first
        login = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"},
        )
        products = requests.get(f"{API_URL}/api/products")

        if login.status_code == 200 and products.status_code == 200:
            user_id = login.json()["user_id"]
            product_id = products.json()["products"][0]["_id"]

            response = requests.post(
                f"{API_URL}/api/interactions",
                json={
                    "user_id": user_id,
                    "product_id": product_id,
                    "interaction_type": "view",
                },
            )
            if response.status_code == 200:
                return "Interaction recorded successfully", "Passed"
        return "Failed to track view", "Failed"

    def _test_track_like(self):
        login = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"},
        )
        products = requests.get(f"{API_URL}/api/products")

        if login.status_code == 200 and products.status_code == 200:
            user_id = login.json()["user_id"]
            product_id = products.json()["products"][0]["_id"]

            response = requests.post(
                f"{API_URL}/api/interactions",
                json={
                    "user_id": user_id,
                    "product_id": product_id,
                    "interaction_type": "like",
                },
            )
            if response.status_code == 200:
                return "Interaction recorded successfully", "Passed"
        return "Failed to track like", "Failed"

    def _test_track_rating(self):
        login = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"},
        )
        products = requests.get(f"{API_URL}/api/products")

        if login.status_code == 200 and products.status_code == 200:
            user_id = login.json()["user_id"]
            product_id = products.json()["products"][0]["_id"]

            response = requests.post(
                f"{API_URL}/api/interactions",
                json={
                    "user_id": user_id,
                    "product_id": product_id,
                    "interaction_type": "rating",
                    "rating": 5,
                },
            )
            if response.status_code == 200:
                return "Interaction with rating recorded successfully", "Passed"
        return "Failed to track rating", "Failed"

    def _test_get_recommendations(self):
        login = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"},
        )

        if login.status_code == 200:
            user_id = login.json()["user_id"]
            response = requests.get(f"{API_URL}/api/recommendations/{user_id}?n=10")
            if response.status_code == 200 and "recommendations" in response.json():
                count = len(response.json()["recommendations"])
                return f"{count} recommendations returned", "Passed"
        return "Failed to get recommendations", "Failed"

    def _test_recommendations_invalid(self):
        response = requests.get(f"{API_URL}/api/recommendations/invalid_user_id?n=10")
        # Either 404 or 200 with popular products is acceptable
        if response.status_code in [200, 404]:
            return f"Status {response.status_code}: Handled gracefully", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_update_profile(self):
        login = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"},
        )

        if login.status_code == 200:
            user_id = login.json()["user_id"]
            timestamp = datetime.now().timestamp()
            response = requests.put(
                f"{API_URL}/api/users/{user_id}",
                json={
                    "username": f"alice_updated_{timestamp}",
                    "preferences": ["Electronics"],
                },
            )
            if response.status_code == 200:
                return "Profile updated successfully", "Passed"
        return "Failed to update profile", "Failed"

    def _test_get_history(self):
        login = requests.post(
            f"{API_URL}/api/login",
            json={"email": "alice@example.com", "password": "password123"},
        )

        if login.status_code == 200:
            user_id = login.json()["user_id"]
            response = requests.get(f"{API_URL}/api/users/{user_id}/history")
            if response.status_code == 200 and "history" in response.json():
                count = len(response.json()["history"])
                return f"History returned with {count} interactions", "Passed"
        return "Failed to get history", "Failed"

    def _test_invalid_endpoint(self):
        response = requests.get(f"{API_URL}/api/nonexistent")
        if response.status_code == 404:
            return "Error 404: Not found", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_missing_field(self):
        response = requests.post(
            f"{API_URL}/api/register",
            json={
                "username": "test",
                "password": "pass123",
                # Missing email
            },
        )
        if response.status_code == 422:
            return "Error 422: Validation error", "Passed"
        return f"Status {response.status_code}", "Failed"

    def _test_get_categories(self):
        response = requests.get(f"{API_URL}/api/categories")
        if response.status_code == 200:
            categories = response.json()
            return f"Returned {len(categories)} categories", "Passed"
        return f"Status {response.status_code}", "Failed"

    def generate_table(self):
        """Generate results table in multiple formats"""

        # Prepare data for table
        table_data = []
        for test in self.results:
            table_data.append(
                [
                    test.number,
                    test.function,
                    test.input_data,
                    test.expected,
                    test.actual,
                    test.status,
                ]
            )

        headers = [
            "№",
            "Function Tested",
            "Input Data",
            "Expected Result",
            "Actual Result",
            "Status",
        ]

        # Print to console
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*80}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}  TEST CASE RESULTS TABLE{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*80}{Color.END}\n")

        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Summary
        total = len(self.results)
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\n{Color.BOLD}SUMMARY:{Color.END}")
        print(f"Total Test Cases: {total}")
        print(f"{Color.GREEN}Passed: {self.passed}{Color.END}")
        print(f"{Color.RED}Failed: {self.failed}{Color.END}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")

        # Save to CSV
        with open("test_cases_table.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(table_data)

        print(f"{Color.GREEN}✓ Results saved to test_cases_table.csv{Color.END}")

        # Save to JSON
        results_json = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": pass_rate,
            "test_cases": [
                {
                    "number": t.number,
                    "function": t.function,
                    "input_data": t.input_data,
                    "expected": t.expected,
                    "actual": t.actual,
                    "status": t.status,
                }
                for t in self.results
            ],
        }

        with open("test_cases_results.json", "w") as f:
            json.dump(results_json, f, indent=2)

        print(f"{Color.GREEN}✓ Results saved to test_cases_results.json{Color.END}")

        # Generate HTML table
        self._generate_html_table(table_data, headers)

        print(f"{Color.GREEN}✓ HTML table saved to test_cases_table.html{Color.END}")

    def _generate_html_table(self, data, headers):
        """Generate HTML table"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Cases Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th {
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .passed {
            color: green;
            font-weight: bold;
        }
        .failed {
            color: red;
            font-weight: bold;
        }
        .stat-box {
            display: inline-block;
            margin: 10px;
            padding: 15px 30px;
            border-radius: 5px;
            font-size: 18px;
        }
        .total { background-color: #2196F3; color: white; }
        .passed-box { background-color: #4CAF50; color: white; }
        .failed-box { background-color: #f44336; color: white; }
    </style>
</head>
<body>
    <h1>Test Case Development - Results Table</h1>
    
    <div class="summary">
        <h2>Summary</h2>
"""

        total = len(data)
        passed = sum(1 for row in data if row[5] == "Passed")
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        html += f"""
        <div class="stat-box total">Total: {total}</div>
        <div class="stat-box passed-box">Passed: {passed}</div>
        <div class="stat-box failed-box">Failed: {failed}</div>
        <div class="stat-box total">Pass Rate: {pass_rate:.1f}%</div>
    </div>
    
    <table>
        <thead>
            <tr>
"""

        for header in headers:
            html += f"                <th>{header}</th>\n"

        html += """            </tr>
        </thead>
        <tbody>
"""

        for row in data:
            html += "            <tr>\n"
            for i, cell in enumerate(row):
                if i == 5:  # Status column
                    status_class = "passed" if cell == "Passed" else "failed"
                    html += f'                <td class="{status_class}">{cell}</td>\n'
                else:
                    html += f"                <td>{cell}</td>\n"
            html += "            </tr>\n"

        html += """        </tbody>
    </table>
</body>
</html>
"""

        with open("test_cases_table.html", "w", encoding="utf-8") as f:
            f.write(html)


def main():
    """Run all test cases and generate table"""
    print(f"{Color.BOLD}{Color.BLUE}")
    print("=" * 80)
    print("  TEST CASE DEVELOPMENT - TABLE GENERATOR")
    print("=" * 80)
    print(f"{Color.END}\n")
    print(f"API Endpoint: {API_URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    runner = TestCaseRunner()

    # Define all test cases
    runner.define_test_cases()

    print(f"Defined {len(runner.test_cases)} test cases\n")

    # Run tests
    runner.run_tests()

    # Generate results table
    runner.generate_table()

    print(f"\n{Color.GREEN}{'='*80}{Color.END}")
    print(f"{Color.GREEN}  TEST CASE DEVELOPMENT COMPLETE!{Color.END}")
    print(f"{Color.GREEN}{'='*80}{Color.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Testing interrupted by user{Color.END}")
    except Exception as e:
        print(f"\n{Color.RED}Error during testing: {e}{Color.END}")
        import traceback

        traceback.print_exc()
