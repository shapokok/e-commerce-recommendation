# Project Structure

This document describes the organized structure of the e-commerce recommendation system.

## Directory Layout

```
ecommerce-recommendation/
│
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app setup and configuration
│   ├── database.py              # MongoDB connection and collections
│   │
│   ├── api/                     # API routes (organized by domain)
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── users.py             # User management endpoints
│   │   ├── products.py          # Product endpoints
│   │   ├── cart.py              # Shopping cart endpoints
│   │   ├── orders.py            # Order endpoints
│   │   ├── admin.py             # Admin endpoints
│   │   └── recommendations.py   # Recommendation endpoints
│   │
│   ├── models/                  # Pydantic models and schemas
│   │   ├── __init__.py
│   │   └── schemas.py           # Request/response validation models
│   │
│   └── services/                # Business logic layer
│       ├── __init__.py
│       └── auth.py              # Authentication utilities
│
├── tests/                       # Test files
│   ├── t1_test_case_table_generator.py
│   ├── t2_generate_test_case_report.py
│   ├── t2_E-Commerce_API_Tests.postman_collection.json
│   ├── t3_locustfile_fixed.py
│   ├── t3_run_fixed_load_tests.py
│   ├── t3_generate_final_load_report.py
│   ├── t4_test_database_complete.py
│   ├── t5_test_recommendation_quality.py
│   ├── t5_test_recommendation_quality_v2.py
│   └── t5_test_recommendation_quality_backup.py
│
├── scripts/                     # Utility scripts (currently empty)
│
├── static/                      # Frontend files
│   └── index.html               # Main frontend application
│
├── data/                        # JSON data files
│   ├── users.json
│   ├── products.json
│   ├── interactions.json
│   ├── carts.json
│   ├── orders.json
│   └── password_reset_tokens.json
│
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── STRUCTURE.md                 # This file
```

## Key Changes

### 1. Modular API Structure
- Routes are now organized by domain (auth, users, products, etc.)
- Each domain has its own router file
- Easier to maintain and extend

### 2. Separation of Concerns
- **Models** (`app/models/`): Data validation schemas
- **Services** (`app/services/`): Business logic
- **API** (`app/api/`): HTTP endpoints
- **Database** (`app/database.py`): Data access layer

### 3. Organized Test Files
- All test files moved to `tests/` directory
- Clear naming convention (t1, t2, t3, etc.)

### 4. Frontend Separation
- Frontend files in `static/` directory
- Clear separation from backend code

## Running the Application

### Start the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Import structure:
```python
# Import from app package
from app.database import db, users_collection
from app.models.schemas import UserRegister
from app.services.auth import hash_password
from app.api import auth, users, products
```

## Benefits of This Structure

1. **Scalability**: Easy to add new features without cluttering
2. **Maintainability**: Clear separation of concerns
3. **Testability**: Tests are organized and easy to find
4. **Readability**: Clear project structure for new developers
5. **Best Practices**: Follows Python package structure conventions

