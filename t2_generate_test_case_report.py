"""
Generate Test Case Report for Assignment
Runs API tests and creates formatted table
"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

print("="*80)
print("  GENERATING TEST CASE REPORT FOR ASSIGNMENT")
print("="*80)

test_results = []
test_num = 1

# Test 1: User Registration (Valid)
print(f"\n[Test {test_num}] User Registration (Valid)...")
try:
    timestamp = int(time.time())
    data = {
        "username": f"test_user_{timestamp}",
        "email": f"test_{timestamp}@mail.com",
        "password": "TestPass123",
        "preferences": ["Electronics", "Books"]
    }
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/register", json=data, timeout=5)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "User Registration",
        "input": f"Username: test_user_{timestamp}, Email: test_{timestamp}@mail.com, Password: ***",
        "expected": "New user successfully registered, user_id returned",
        "actual": f"Status {response.status_code}, User created" if response.status_code == 200 else f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 200 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "User Registration",
        "input": "Valid user data",
        "expected": "User registered",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })
    print(f"  Result: FAILED - {e}")

test_num += 1

# Test 2: User Registration (Duplicate Email)
print(f"\n[Test {test_num}] User Registration (Duplicate Email)...")
try:
    data = {
        "username": "duplicate_user",
        "email": "alice@example.com",  # Existing email
        "password": "password123"
    }
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/register", json=data, timeout=5)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "User Registration (Duplicate)",
        "input": "Username: duplicate_user, Email: alice@example.com (existing)",
        "expected": "Error 400 - Email already registered",
        "actual": f"Status {response.status_code}, {response.json().get('detail', '')}",
        "status": "PASSED" if response.status_code == 400 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "User Registration (Duplicate)",
        "input": "Duplicate email",
        "expected": "Error 400",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 3: User Login (Valid)
print(f"\n[Test {test_num}] User Login (Valid)...")
try:
    data = {
        "email": "alice@example.com",
        "password": "password123"
    }
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/login", json=data, timeout=5)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "User Login",
        "input": "Email: alice@example.com, Password: ***",
        "expected": "Status 200, user_id and username returned",
        "actual": f"Status {response.status_code}, Login successful" if response.status_code == 200 else f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 200 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    if response.status_code == 200:
        user_id = response.json().get('user_id')
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "User Login",
        "input": "Valid credentials",
        "expected": "Login successful",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 4: User Login (Invalid Password)
print(f"\n[Test {test_num}] User Login (Invalid Password)...")
try:
    data = {
        "email": "alice@example.com",
        "password": "wrongpassword"
    }
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/login", json=data, timeout=5)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "User Login (Invalid)",
        "input": "Email: alice@example.com, Password: wrongpassword",
        "expected": "Error 401 - Invalid credentials",
        "actual": f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 401 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "User Login (Invalid)",
        "input": "Wrong password",
        "expected": "Error 401",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 5: Get Products
print(f"\n[Test {test_num}] Get Products...")
try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/products", timeout=5)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "Get Products",
        "input": "GET /api/products",
        "expected": "Status 200, list of products returned",
        "actual": f"Status {response.status_code}, {response.json().get('count', 0)} products" if response.status_code == 200 else f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 200 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "Get Products",
        "input": "GET request",
        "expected": "Products list",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 6: Search Products
print(f"\n[Test {test_num}] Search Products...")
try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/products?search=laptop", timeout=5)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "Search Products",
        "input": "search=laptop",
        "expected": "Status 200, filtered products",
        "actual": f"Status {response.status_code}, {response.json().get('count', 0)} products found" if response.status_code == 200 else f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 200 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "Search Products",
        "input": "search query",
        "expected": "Filtered results",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 7: Get Recommendations (Valid User)
print(f"\n[Test {test_num}] Get Recommendations...")
try:
    # Get a real user ID first
    users = requests.get(f"{BASE_URL}/api/products", timeout=5)
    # Use alice's ID
    user_id = "69163feb191d7464360b8c5c"  # Example user ID

    start = time.time()
    response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}?n=5", timeout=10)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "Get Recommendations",
        "input": f"user_id: {user_id}, n=5",
        "expected": "Status 200, 5 recommendations returned",
        "actual": f"Status {response.status_code}, {response.json().get('count', 0)} recommendations" if response.status_code == 200 else f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 200 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "Get Recommendations",
        "input": "Valid user_id",
        "expected": "Recommendations list",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 8: Get Recommendations (Invalid User)
print(f"\n[Test {test_num}] Get Recommendations (Invalid User)...")
try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/recommendations/invalid_id?n=5", timeout=10)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "Get Recommendations (Invalid)",
        "input": "user_id: invalid_id",
        "expected": "Error 404 - User not found",
        "actual": f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 404 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "Get Recommendations (Invalid)",
        "input": "Invalid user_id",
        "expected": "Error 404",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 9: Get Popular Products
print(f"\n[Test {test_num}] Get Popular Products...")
try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/recommendations/popular?n=10", timeout=10)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "Get Popular Products",
        "input": "n=10",
        "expected": "Status 200, 10 popular products",
        "actual": f"Status {response.status_code}, {response.json().get('count', 0)} products" if response.status_code == 200 else f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 200 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "Get Popular Products",
        "input": "n=10",
        "expected": "Popular products",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

test_num += 1

# Test 10: Invalid Endpoint
print(f"\n[Test {test_num}] Invalid Endpoint...")
try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/nonexistent", timeout=5)
    elapsed = (time.time() - start) * 1000

    test_results.append({
        "num": test_num,
        "function": "Invalid Endpoint",
        "input": "GET /api/nonexistent",
        "expected": "Error 404 - Not Found",
        "actual": f"Status {response.status_code}",
        "status": "PASSED" if response.status_code == 404 else "FAILED",
        "response_time": f"{elapsed:.0f}ms"
    })
    print(f"  Result: {test_results[-1]['status']} ({elapsed:.0f}ms)")
except Exception as e:
    test_results.append({
        "num": test_num,
        "function": "Invalid Endpoint",
        "input": "Invalid URL",
        "expected": "Error 404",
        "actual": f"Error: {str(e)}",
        "status": "FAILED",
        "response_time": "N/A"
    })

# Generate Report
print("\n" + "="*80)
print("  TEST RESULTS SUMMARY")
print("="*80)

passed = sum(1 for t in test_results if t['status'] == 'PASSED')
failed = sum(1 for t in test_results if t['status'] == 'FAILED')

print(f"\nTotal Tests: {len(test_results)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Pass Rate: {(passed/len(test_results)*100):.1f}%")

# Save to file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save as Markdown
with open(f"test_case_report_{timestamp}.md", "w", encoding="utf-8") as f:
    f.write("# Test Case Report - E-Commerce Recommendation System\n\n")
    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"**Summary:** {passed}/{len(test_results)} tests passed ({(passed/len(test_results)*100):.1f}%)\n\n")
    f.write("## Test Results\n\n")
    f.write("| № | Function Tested | Input Data | Expected Result | Actual Result | Status | Response Time |\n")
    f.write("|---|----------------|------------|-----------------|---------------|--------|---------------|\n")
    for test in test_results:
        f.write(f"| {test['num']} | {test['function']} | {test['input']} | {test['expected']} | {test['actual']} | {test['status']} | {test['response_time']} |\n")

print(f"\n✓ Report saved to: test_case_report_{timestamp}.md")

# Save as JSON
with open(f"test_case_results_{timestamp}.json", "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(test_results),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed/len(test_results)*100, 1)
        },
        "tests": test_results
    }, f, indent=2)

print(f"✓ JSON results saved to: test_case_results_{timestamp}.json")
print("="*80)
