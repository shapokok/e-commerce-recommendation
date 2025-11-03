import requests
import time
import statistics
from pymongo import MongoClient
from datetime import datetime
import json

API_URL = "http://localhost:8000"
MONGO_URI = "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_api_endpoint(endpoint, method="GET", data=None, iterations=10):
    """Test API endpoint performance"""
    times = []
    
    for i in range(iterations):
        start = time.time()
        
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{API_URL}{endpoint}", json=data)
        
        end = time.time()
        elapsed = (end - start) * 1000  # Convert to ms
        times.append(elapsed)
        
        if response.status_code not in [200, 201]:
            print(f"Error on iteration {i+1}: {response.status_code}")
    
    return times

def analyze_times(times, endpoint_name):
    """Analyze and print timing statistics"""
    avg = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    median = statistics.median(times)
    
    print(f"\n{endpoint_name}:")
    print(f"  Average: {avg:.2f}ms")
    print(f"  Median:  {median:.2f}ms")
    print(f"  Min:     {min_time:.2f}ms")
    print(f"  Max:     {max_time:.2f}ms")
    
    return {
        "endpoint": endpoint_name,
        "average": avg,
        "median": median,
        "min": min_time,
        "max": max_time
    }

def test_database_performance():
    """Test MongoDB query performance"""
    print_header("DATABASE PERFORMANCE TESTS")
    
    client = MongoClient(MONGO_URI)
    db = client.ecommerce_db
    
    results = []
    
    # Test 1: Count users
    start = time.time()
    user_count = db.users.count_documents({})
    elapsed = (time.time() - start) * 1000
    print(f"\nCount users: {elapsed:.2f}ms ({user_count} users)")
    results.append({"test": "Count users", "time": elapsed, "count": user_count})
    
    # Test 2: Count products
    start = time.time()
    product_count = db.products.count_documents({})
    elapsed = (time.time() - start) * 1000
    print(f"Count products: {elapsed:.2f}ms ({product_count} products)")
    results.append({"test": "Count products", "time": elapsed, "count": product_count})
    
    # Test 3: Count interactions
    start = time.time()
    interaction_count = db.interactions.count_documents({})
    elapsed = (time.time() - start) * 1000
    print(f"Count interactions: {elapsed:.2f}ms ({interaction_count} interactions)")
    results.append({"test": "Count interactions", "time": elapsed, "count": interaction_count})
    
    # Test 4: Find products by category
    start = time.time()
    electronics = list(db.products.find({"category": "Electronics"}))
    elapsed = (time.time() - start) * 1000
    print(f"Find Electronics: {elapsed:.2f}ms ({len(electronics)} products)")
    results.append({"test": "Find by category", "time": elapsed, "count": len(electronics)})
    
    # Test 5: Aggregation - popular products
    start = time.time()
    pipeline = [
        {"$group": {"_id": "$product_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    popular = list(db.interactions.aggregate(pipeline))
    elapsed = (time.time() - start) * 1000
    print(f"Aggregate popular products: {elapsed:.2f}ms")
    results.append({"test": "Aggregation", "time": elapsed})
    
    return results

def test_api_performance():
    """Test API endpoint performance"""
    print_header("API PERFORMANCE TESTS")
    
    # Get a test user ID
    response = requests.get(f"{API_URL}/api/products")
    if response.status_code != 200:
        print("Error: Cannot connect to API. Make sure server is running!")
        return []
    
    results = []
    
    # Test 1: Get all products
    times = test_api_endpoint("/api/products", iterations=10)
    result = analyze_times(times, "GET /api/products")
    results.append(result)
    
    # Test 2: Get categories
    times = test_api_endpoint("/api/categories", iterations=10)
    result = analyze_times(times, "GET /api/categories")
    results.append(result)
    
    # Test 3: Search products
    times = test_api_endpoint("/api/products?search=laptop", iterations=10)
    result = analyze_times(times, "GET /api/products?search=laptop")
    results.append(result)
    
    # Test 4: Filter by category
    times = test_api_endpoint("/api/products?category=Electronics", iterations=10)
    result = analyze_times(times, "GET /api/products?category=Electronics")
    results.append(result)
    
    # Get a user for recommendation testing
    try:
        login_data = {"email": "alice@example.com", "password": "password123"}
        login_response = requests.post(f"{API_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            user_id = login_response.json()["user_id"]
            
            # Test 5: Get recommendations
            times = test_api_endpoint(f"/api/recommendations/{user_id}?n=10", iterations=10)
            result = analyze_times(times, "GET /api/recommendations")
            results.append(result)
    except Exception as e:
        print(f"Could not test recommendations: {e}")
    
    return results

def test_recommendation_scalability():
    """Test recommendation system with varying data sizes"""
    print_header("RECOMMENDATION SCALABILITY TEST")
    
    try:
        login_data = {"email": "alice@example.com", "password": "password123"}
        login_response = requests.post(f"{API_URL}/api/login", json=login_data)
        if login_response.status_code != 200:
            print("Cannot login for testing")
            return
        
        user_id = login_response.json()["user_id"]
        
        # Test with different numbers of recommendations
        recommendation_counts = [5, 10, 20, 50]
        
        for n in recommendation_counts:
            times = []
            for _ in range(5):
                start = time.time()
                response = requests.get(f"{API_URL}/api/recommendations/{user_id}?n={n}")
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
            
            avg = statistics.mean(times)
            print(f"\nRecommendations (n={n}): {avg:.2f}ms average")
    
    except Exception as e:
        print(f"Error in scalability test: {e}")

def generate_report(api_results, db_results):
    """Generate performance report"""
    print_header("PERFORMANCE ANALYSIS REPORT")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "api_tests": api_results,
        "database_tests": db_results
    }
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 60)
    
    if api_results:
        api_avg = statistics.mean([r["average"] for r in api_results])
        print(f"Average API Response Time: {api_avg:.2f}ms")
        
        fastest = min(api_results, key=lambda x: x["average"])
        slowest = max(api_results, key=lambda x: x["average"])
        print(f"Fastest Endpoint: {fastest['endpoint']} ({fastest['average']:.2f}ms)")
        print(f"Slowest Endpoint: {slowest['endpoint']} ({slowest['average']:.2f}ms)")
    
    if db_results:
        db_avg = statistics.mean([r["time"] for r in db_results])
        print(f"\nAverage Database Query Time: {db_avg:.2f}ms")
    
    # Recommendations
    print("\n💡 OPTIMIZATION RECOMMENDATIONS")
    print("-" * 60)
    
    if api_results:
        for result in api_results:
            if result["average"] > 500:
                print(f"⚠️  {result['endpoint']} is slow (>{result['average']:.0f}ms)")
                print(f"   Consider: caching, indexing, or query optimization")
            elif result["average"] > 200:
                print(f"⚡ {result['endpoint']} could be faster ({result['average']:.0f}ms)")
            else:
                print(f"✅ {result['endpoint']} performs well ({result['average']:.0f}ms)")
    
    # Save report
    with open('performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n📄 Full report saved to: performance_report.json")

def main():
    print_header("E-COMMERCE PERFORMANCE TESTING SUITE")
    print(f"Testing API at: {API_URL}")
    print(f"Testing Database: MongoDB Atlas")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Run tests
    db_results = test_database_performance()
    api_results = test_api_performance()
    test_recommendation_scalability()
    
    # Generate report
    generate_report(api_results, db_results)
    
    print_header("TESTING COMPLETE")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()