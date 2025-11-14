# E-Commerce API - Project Files Overview

## Main Application Files

### Core Backend
- **`main.py`** - Main FastAPI application with all endpoints (users, products, cart, orders, admin)
- **`database.py`** - MongoDB connection and collection setup
- **`recommendation_routes.py`** - Recommendation system endpoints (collaborative, content-based, hybrid)

### Frontend
- **`index.html`** - Main user interface
- **Admin pages** (in subdirectories)

### Configuration
- **`requirements.txt`** - Python dependencies

---

## Testing Files by Category

### 1. API Testing (Functional & Non-Functional)

**Files Needed:**
- **`test_functional.py`** - Tests all API endpoints (register, login, products, cart, checkout, etc.)
- **`api_automated_tests.py`** - Automated API test suite
- **`E-Commerce_API_Tests.postman_collection.json`** - Postman collection for manual testing

**What They Test:**
- User registration/login
- Product CRUD operations
- Cart functionality
- Order checkout
- Recommendations
- Admin endpoints

---

### 2. Recommendation Quality Testing

**Files Needed:**
- **`test_recommendation_quality.py`** - Tests recommendation algorithms

**What It Tests:**
- Collaborative filtering accuracy
- Content-based filtering relevance
- Hybrid algorithm performance
- Precision, recall, diversity metrics

**Output:**
- `recommendation_quality_results.json`

---

### 3. Load/Performance Testing

**Files Needed:**
- **`locustfile.py`** - Locust load testing configuration
- **`performance_test.py`** - Performance test runner

**What It Tests:**
- System under concurrent users (50, 100, 500)
- Response times
- Requests per second (RPS)
- Failure rates

**Output:**
- `Load_Testing_Report.html`
- `stats_*_users_*.csv`

---

### 4. Database Testing

**Files Needed:**
- **`test_database_complete.py`** - Complete database testing suite

**What It Tests:**
- **Data Integrity:** Updates, deletions, cascading
- **Performance:** Query profiling, slow query detection
- **Indexing:** Index verification with explain()
- **Caching:** WiredTiger cache effectiveness

**Output:**
- `database_test_results_complete.json`
- `database_test_report.md`

---

## Quick Reference: Run Each Test

```bash
# 1. Functional API Tests
python test_functional.py

# 2. Recommendation Quality
python test_recommendation_quality.py

# 3. Load/Performance Tests
python performance_test.py
# or
locust -f locustfile.py --users 100 --spawn-rate 10 --run-time 60s --host http://localhost:8000

# 4. Database Tests
python test_database_complete.py
```

---

## Complete File Structure

```
e-com/
├── Backend
│   ├── main.py                          # Main API
│   ├── database.py                      # DB connection
│   └── recommendation_routes.py         # Recommendations
│
├── Testing Files
│   ├── test_functional.py               # Functional tests
│   ├── test_recommendation_quality.py   # Recommendation tests
│   ├── performance_test.py              # Performance tests
│   ├── locustfile.py                    # Load tests
│   └── test_database_complete.py        # Database tests
│
├── Test Results
│   ├── functional_test_results.json
│   ├── recommendation_quality_results.json
│   ├── Load_Testing_Report.html
│   └── database_test_results_complete.json
│
├── API Documentation
│   ├── E-Commerce_API_Tests.postman_collection.json
│   └── API_TESTING_DOCUMENTATION.md
│
└── Configuration
    └── requirements.txt
```

---

## Dependencies (requirements.txt)

```txt
fastapi
uvicorn
pymongo
bcrypt
pydantic[email]
locust
requests
numpy
scikit-learn
```

---

## Summary: Files Needed for Each Assignment Part

| Assignment | Main Files | Output Files |
|------------|------------|--------------|
| **API Testing** | `test_functional.py` | `functional_test_results.json` |
| **Recommendations** | `test_recommendation_quality.py` | `recommendation_quality_results.json` |
| **Load Testing** | `locustfile.py`, `performance_test.py` | `Load_Testing_Report.html` |
| **Database Testing** | `test_database_complete.py` | `database_test_report.md` |

---

**Total Core Files:** 8 (3 backend + 5 testing)
**All tests automated and generate detailed reports!**
