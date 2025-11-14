"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import (
    users_collection,
    products_collection,
    interactions_collection,
    carts_collection,
    orders_collection,
)

# Import routers
from app.api import auth, users, products, cart, orders, admin, recommendations

app = FastAPI(title="E-commerce Recommendation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "E-commerce Recommendation API",
        "status": "running",
        "optimizations_active": True,
        "connection_pool": "ENABLED",
        "max_pool_size": 50
    }


# Database indexes for performance
def create_indexes():
    """Create database indexes for better query performance"""
    try:
        print("[OPTIMIZATION] Creating database indexes...")
        users_collection.create_index([("email", 1)], unique=True)
        users_collection.create_index([("username", 1)])
        products_collection.create_index([("category", 1)])
        products_collection.create_index([("name", "text")])
        interactions_collection.create_index([("user_id", 1)])
        interactions_collection.create_index([("product_id", 1)])
        interactions_collection.create_index([("user_id", 1), ("timestamp", -1)])
        interactions_collection.create_index([("interaction_type", 1)])
        carts_collection.create_index([("user_id", 1)])
        orders_collection.create_index([("user_id", 1)])
        orders_collection.create_index([("created_at", -1)])
        print("[OPTIMIZATION] Database indexes created successfully")
    except Exception as e:
        print(f"[OPTIMIZATION] Warning: Some indexes may already exist: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize database indexes on startup"""
    print("\n" + "="*60)
    print("[OPTIMIZATION] FASTAPI SERVER STARTING WITH OPTIMIZATIONS")
    print("="*60)
    create_indexes()
    print("="*60)
    print("[OPTIMIZATION] Server is ready with optimized performance!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

