"""
Database Testing Suite
Tests MongoDB database integrity, performance, indexing, and query optimization
"""

from pymongo import MongoClient
from bson import ObjectId
import time
import json
from datetime import datetime
from typing import List, Dict

MONGO_URI = "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

class DatabaseTester:
    """Test MongoDB database operations and performance"""
    
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.ecommerce_db
        self.results = {
            "integrity_tests": [],
            "performance_tests": [],
            "index_tests": [],
            "query_optimization": []
        }
    
    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}  {title}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}\n")
    
    def test_data_integrity(self):
        """Test referential integrity and data consistency"""
        self.print_header("DATA INTEGRITY TESTS")
        
        users_collection = self.db.users
        products_collection = self.db.products
        interactions_collection = self.db.interactions
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Check for orphaned interactions (user doesn't exist)
        print("Test 1: Checking for orphaned user interactions...")
        tests_total += 1
        
        all_user_ids = set(str(user["_id"]) for user in users_collection.find({}, {"_id": 1}))
        orphaned_user_interactions = interactions_collection.count_documents({
            "user_id": {"$nin": list(all_user_ids)}
        })
        
        if orphaned_user_interactions == 0:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - No orphaned user interactions")
            tests_passed += 1
            status = "PASSED"
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Found {orphaned_user_interactions} orphaned interactions")
            status = "FAILED"
        
        self.results["integrity_tests"].append({
            "test": "Orphaned user interactions",
            "status": status,
            "orphaned_count": orphaned_user_interactions
        })
        
        # Test 2: Check for orphaned interactions (product doesn't exist)
        print("\nTest 2: Checking for orphaned product interactions...")
        tests_total += 1
        
        all_product_ids = set(str(prod["_id"]) for prod in products_collection.find({}, {"_id": 1}))
        orphaned_product_interactions = interactions_collection.count_documents({
            "product_id": {"$nin": list(all_product_ids)}
        })
        
        if orphaned_product_interactions == 0:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - No orphaned product interactions")
            tests_passed += 1
            status = "PASSED"
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Found {orphaned_product_interactions} orphaned interactions")
            status = "FAILED"
        
        self.results["integrity_tests"].append({
            "test": "Orphaned product interactions",
            "status": status,
            "orphaned_count": orphaned_product_interactions
        })
        
        # Test 3: Check for duplicate users (by email)
        print("\nTest 3: Checking for duplicate user emails...")
        tests_total += 1
        
        pipeline = [
            {"$group": {"_id": "$email", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(users_collection.aggregate(pipeline))
        
        if len(duplicates) == 0:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - No duplicate emails")
            tests_passed += 1
            status = "PASSED"
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Found {len(duplicates)} duplicate emails")
            status = "FAILED"
        
        self.results["integrity_tests"].append({
            "test": "Duplicate user emails",
            "status": status,
            "duplicate_count": len(duplicates)
        })
        
        # Test 4: Check for valid interaction types
        print("\nTest 4: Checking interaction types validity...")
        tests_total += 1
        
        valid_types = ["view", "like", "rating"]
        invalid_interactions = interactions_collection.count_documents({
            "interaction_type": {"$nin": valid_types}
        })
        
        if invalid_interactions == 0:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - All interaction types are valid")
            tests_passed += 1
            status = "PASSED"
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Found {invalid_interactions} invalid interaction types")
            status = "FAILED"
        
        self.results["integrity_tests"].append({
            "test": "Valid interaction types",
            "status": status,
            "invalid_count": invalid_interactions
        })
        
        # Test 5: Check for ratings in valid range (1-5)
        print("\nTest 5: Checking rating values...")
        tests_total += 1
        
        invalid_ratings = interactions_collection.count_documents({
            "interaction_type": "rating",
            "$or": [
                {"rating": {"$lt": 1}},
                {"rating": {"$gt": 5}},
                {"rating": None}
            ]
        })
        
        if invalid_ratings == 0:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - All ratings are in valid range (1-5)")
            tests_passed += 1
            status = "PASSED"
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Found {invalid_ratings} invalid ratings")
            status = "FAILED"
        
        self.results["integrity_tests"].append({
            "test": "Valid rating values",
            "status": status,
            "invalid_count": invalid_ratings
        })
        
        print(f"\n{Color.BOLD}Integrity Tests: {tests_passed}/{tests_total} passed{Color.END}")
    
    def test_query_performance(self):
        """Test database query performance"""
        self.print_header("QUERY PERFORMANCE TESTS")
        
        users_collection = self.db.users
        products_collection = self.db.products
        interactions_collection = self.db.interactions
        
        # Test 1: Simple find query
        print("Test 1: Find user by email...")
        start = time.time()
        user = users_collection.find_one({"email": "alice@example.com"})
        elapsed = (time.time() - start) * 1000
        
        print(f"  Time: {elapsed:.2f}ms")
        if elapsed < 50:
            print(f"  {Color.GREEN}✓ EXCELLENT{Color.END} - Query is very fast")
        elif elapsed < 100:
            print(f"  {Color.YELLOW}○ GOOD{Color.END} - Query is acceptable")
        else:
            print(f"  {Color.RED}✗ SLOW{Color.END} - Query needs optimization")
        
        self.results["performance_tests"].append({
            "test": "Find user by email",
            "time_ms": elapsed,
            "performance": "excellent" if elapsed < 50 else "good" if elapsed < 100 else "slow"
        })
        
        # Test 2: Find products by category
        print("\nTest 2: Find products by category...")
        start = time.time()
        products = list(products_collection.find({"category": "Electronics"}))
        elapsed = (time.time() - start) * 1000
        
        print(f"  Time: {elapsed:.2f}ms ({len(products)} products)")
        if elapsed < 50:
            print(f"  {Color.GREEN}✓ EXCELLENT{Color.END}")
        elif elapsed < 100:
            print(f"  {Color.YELLOW}○ GOOD{Color.END}")
        else:
            print(f"  {Color.RED}✗ SLOW{Color.END}")
        
        self.results["performance_tests"].append({
            "test": "Find products by category",
            "time_ms": elapsed,
            "result_count": len(products),
            "performance": "excellent" if elapsed < 50 else "good" if elapsed < 100 else "slow"
        })
        
        # Test 3: Count user interactions
        print("\nTest 3: Count user interactions...")
        if user:
            start = time.time()
            count = interactions_collection.count_documents({"user_id": str(user["_id"])})
            elapsed = (time.time() - start) * 1000
            
            print(f"  Time: {elapsed:.2f}ms ({count} interactions)")
            if elapsed < 50:
                print(f"  {Color.GREEN}✓ EXCELLENT{Color.END}")
            elif elapsed < 100:
                print(f"  {Color.YELLOW}○ GOOD{Color.END}")
            else:
                print(f"  {Color.RED}✗ SLOW{Color.END}")
            
            self.results["performance_tests"].append({
                "test": "Count user interactions",
                "time_ms": elapsed,
                "result_count": count,
                "performance": "excellent" if elapsed < 50 else "good" if elapsed < 100 else "slow"
            })
        
        # Test 4: Aggregation - Popular products
        print("\nTest 4: Aggregate popular products...")
        start = time.time()
        pipeline = [
            {"$group": {"_id": "$product_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        popular = list(interactions_collection.aggregate(pipeline))
        elapsed = (time.time() - start) * 1000
        
        print(f"  Time: {elapsed:.2f}ms ({len(popular)} products)")
        if elapsed < 100:
            print(f"  {Color.GREEN}✓ EXCELLENT{Color.END}")
        elif elapsed < 200:
            print(f"  {Color.YELLOW}○ GOOD{Color.END}")
        else:
            print(f"  {Color.RED}✗ SLOW{Color.END}")
        
        self.results["performance_tests"].append({
            "test": "Aggregate popular products",
            "time_ms": elapsed,
            "result_count": len(popular),
            "performance": "excellent" if elapsed < 100 else "good" if elapsed < 200 else "slow"
        })
        
        # Test 5: Text search
        print("\nTest 5: Text search for products...")
        start = time.time()
        products = list(products_collection.find({
            "$or": [
                {"name": {"$regex": "laptop", "$options": "i"}},
                {"description": {"$regex": "laptop", "$options": "i"}}
            ]
        }))
        elapsed = (time.time() - start) * 1000
        
        print(f"  Time: {elapsed:.2f}ms ({len(products)} products)")
        if elapsed < 100:
            print(f"  {Color.GREEN}✓ EXCELLENT{Color.END}")
        elif elapsed < 200:
            print(f"  {Color.YELLOW}○ GOOD{Color.END}")
        else:
            print(f"  {Color.RED}✗ SLOW{Color.END}")
        
        self.results["performance_tests"].append({
            "test": "Text search",
            "time_ms": elapsed,
            "result_count": len(products),
            "performance": "excellent" if elapsed < 100 else "good" if elapsed < 200 else "slow"
        })
    
    def test_indexes(self):
        """Test database indexes"""
        self.print_header("INDEX TESTS")
        
        # Check indexes on each collection
        collections_to_test = ["users", "products", "interactions"]
        
        for coll_name in collections_to_test:
            collection = self.db[coll_name]
            indexes = list(collection.list_indexes())
            
            print(f"\n{coll_name} collection:")
            print(f"  Total indexes: {len(indexes)}")
            
            index_info = []
            for idx in indexes:
                index_name = idx.get("name", "unknown")
                index_keys = list(idx.get("key", {}).keys())
                unique = idx.get("unique", False)
                
                print(f"  • {index_name}: {', '.join(index_keys)}" + 
                      (f" {Color.GREEN}(UNIQUE){Color.END}" if unique else ""))
                
                index_info.append({
                    "name": index_name,
                    "keys": index_keys,
                    "unique": unique
                })
            
            self.results["index_tests"].append({
                "collection": coll_name,
                "index_count": len(indexes),
                "indexes": index_info
            })
        
        # Recommendations for missing indexes
        print(f"\n{Color.BOLD}INDEX RECOMMENDATIONS:{Color.END}")
        
        users_indexes = [idx["name"] for idx in self.results["index_tests"][0]["indexes"]]
        if "email_1" not in users_indexes:
            print(f"  {Color.YELLOW}• Consider adding unique index on users.email{Color.END}")
        else:
            print(f"  {Color.GREEN}✓ users.email is properly indexed{Color.END}")
        
        products_indexes = [idx["name"] for idx in self.results["index_tests"][1]["indexes"]]
        if "category_1" not in products_indexes:
            print(f"  {Color.YELLOW}• Consider adding index on products.category{Color.END}")
        else:
            print(f"  {Color.GREEN}✓ products.category is properly indexed{Color.END}")
    
    def test_crud_operations(self):
        """Test CRUD operations with data consistency"""
        self.print_header("CRUD OPERATIONS TEST")
        
        products_collection = self.db.products
        
        # Create
        print("Test 1: CREATE operation...")
        test_product = {
            "name": f"Test Product {datetime.now().timestamp()}",
            "description": "Test product for database testing",
            "category": "Test",
            "price": 99.99,
            "created_at": datetime.utcnow()
        }
        
        result = products_collection.insert_one(test_product)
        product_id = result.inserted_id
        
        if product_id:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - Product created with ID: {product_id}")
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Failed to create product")
        
        # Read
        print("\nTest 2: READ operation...")
        found_product = products_collection.find_one({"_id": product_id})
        
        if found_product and found_product["name"] == test_product["name"]:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - Product read successfully")
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Failed to read product")
        
        # Update
        print("\nTest 3: UPDATE operation...")
        update_result = products_collection.update_one(
            {"_id": product_id},
            {"$set": {"price": 149.99}}
        )
        
        updated_product = products_collection.find_one({"_id": product_id})
        
        if update_result.modified_count == 1 and updated_product["price"] == 149.99:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - Product updated successfully")
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Failed to update product")
        
        # Delete
        print("\nTest 4: DELETE operation...")
        delete_result = products_collection.delete_one({"_id": product_id})
        
        deleted_product = products_collection.find_one({"_id": product_id})
        
        if delete_result.deleted_count == 1 and deleted_product is None:
            print(f"  {Color.GREEN}✓ PASSED{Color.END} - Product deleted successfully")
        else:
            print(f"  {Color.RED}✗ FAILED{Color.END} - Failed to delete product")
        
        self.results["crud_tests"] = {
            "create": "passed" if product_id else "failed",
            "read": "passed" if found_product else "failed",
            "update": "passed" if update_result.modified_count == 1 else "failed",
            "delete": "passed" if delete_result.deleted_count == 1 else "failed"
        }
    
    def generate_summary(self):
        """Generate testing summary"""
        self.print_header("DATABASE TESTING SUMMARY")
        
        # Integrity
        integrity_passed = sum(1 for test in self.results["integrity_tests"] if test["status"] == "PASSED")
        integrity_total = len(self.results["integrity_tests"])
        print(f"Data Integrity: {integrity_passed}/{integrity_total} tests passed")
        
        # Performance
        excellent = sum(1 for test in self.results["performance_tests"] if test["performance"] == "excellent")
        good = sum(1 for test in self.results["performance_tests"] if test["performance"] == "good")
        slow = sum(1 for test in self.results["performance_tests"] if test["performance"] == "slow")
        print(f"Query Performance: {excellent} excellent, {good} good, {slow} slow")
        
        # Indexes
        total_indexes = sum(test["index_count"] for test in self.results["index_tests"])
        print(f"Total Indexes: {total_indexes}")
        
        # Overall assessment
        print(f"\n{Color.BOLD}OVERALL ASSESSMENT:{Color.END}")
        
        if integrity_passed == integrity_total:
            print(f"  {Color.GREEN}✓ Data integrity is excellent{Color.END}")
        else:
            print(f"  {Color.YELLOW}⚠ Data integrity issues found{Color.END}")
        
        if slow == 0:
            print(f"  {Color.GREEN}✓ Query performance is good{Color.END}")
        else:
            print(f"  {Color.YELLOW}⚠ Some queries need optimization{Color.END}")
    
    def save_results(self, filename: str = "database_test_results.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{Color.GREEN}Results saved to {filename}{Color.END}")

def main():
    """Run all database tests"""
    print(f"{Color.BOLD}{Color.BLUE}")
    print("="*70)
    print("  DATABASE TESTING SUITE")
    print("="*70)
    print(f"{Color.END}")
    print(f"Database: MongoDB Atlas\n")
    
    tester = DatabaseTester()
    
    # Run all tests
    tester.test_data_integrity()
    tester.test_query_performance()
    tester.test_indexes()
    tester.test_crud_operations()
    
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