from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import bcrypt
from pymongo import MongoClient
from bson import ObjectId
import os

# MongoDB connection
MONGO_URI = "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.ecommerce_db

# Collections
users_collection = db.users
products_collection = db.products
interactions_collection = db.interactions

app = FastAPI(title="E-commerce Recommendation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    preferences: Optional[List[str]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    preferences: Optional[List[str]] = None

class Product(BaseModel):
    name: str
    description: str
    category: str
    price: float
    image_url: Optional[str] = ""

class Interaction(BaseModel):
    user_id: str
    product_id: str
    interaction_type: str  # "view", "like", "rating"
    rating: Optional[int] = None

# Helper function
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Routes
@app.get("/")
def root():
    return {"message": "E-commerce Recommendation API", "status": "running"}

# User Registration
@app.post("/api/register")
def register_user(user: UserRegister):
    # Check if user exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "preferences": user.preferences,
        "created_at": datetime.utcnow()
    }
    
    result = users_collection.insert_one(user_doc)
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
        "username": user.username
    }

# User Login
@app.post("/api/login")
def login_user(credentials: UserLogin):
    user = users_collection.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "username": user["username"]
    }

# Get User Profile
@app.get("/api/users/{user_id}")
def get_user_profile(user_id: str):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
# Update User Profile
@app.put("/api/users/{user_id}")
def update_user_profile(user_id: str, update_data: UserUpdate):
    """Update user profile (username and preferences)"""
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_fields = {}
        
        # Update username if provided
        if update_data.username is not None and update_data.username.strip():
            # Check if username already taken by another user
            existing = users_collection.find_one({
                "username": update_data.username,
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            update_fields["username"] = update_data.username.strip()
        
        # Update preferences if provided
        if update_data.preferences is not None:
            update_fields["preferences"] = update_data.preferences
        
        # Update timestamp
        update_fields["updated_at"] = datetime.utcnow()
        
        # Perform update
        if update_fields:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
        
        # Return updated user
        updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
        updated_user["_id"] = str(updated_user["_id"])
        updated_user.pop("password_hash", None)
        
        return {
            "message": "Profile updated successfully",
            "user": updated_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")
        
# Get User History (all interactions with details)
@app.get("/api/users/{user_id}/history")
def get_user_history(user_id: str, interaction_type: Optional[str] = None):
    """
    Get user's interaction history with product details
    Optional filter by interaction_type: view, like, rating
    """
    try:
        # Build query
        query = {"user_id": user_id}
        if interaction_type:
            query["interaction_type"] = interaction_type
        
        # Get interactions sorted by timestamp (newest first)
        interactions = list(interactions_collection.find(query).sort("timestamp", -1))
        
        # Enrich with product details
        history = []
        for interaction in interactions:
            try:
                product = products_collection.find_one({"_id": ObjectId(interaction["product_id"])})
                if product:
                    history_item = {
                        "_id": str(interaction["_id"]),
                        "interaction_type": interaction["interaction_type"],
                        "rating": interaction.get("rating"),
                        "timestamp": interaction["timestamp"],
                        "product": {
                            "_id": str(product["_id"]),
                            "name": product["name"],
                            "description": product["description"],
                            "category": product["category"],
                            "price": product["price"],
                            "image_url": product.get("image_url", "")
                        }
                    }
                    history.append(history_item)
            except:
                continue
        
        return {
            "user_id": user_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get all products
@app.get("/api/products")
def get_products(category: Optional[str] = None, search: Optional[str] = None):
    query = {}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    products = list(products_collection.find(query).limit(50))
    
    for product in products:
        product["_id"] = str(product["_id"])
    
    return {"products": products, "count": len(products)}

# Get single product
@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product["_id"] = str(product["_id"])
        return product
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

# Create product (for admin/testing)
@app.post("/api/products")
def create_product(product: Product):
    product_doc = product.dict()
    product_doc["created_at"] = datetime.utcnow()
    
    result = products_collection.insert_one(product_doc)
    
    return {
        "message": "Product created",
        "product_id": str(result.inserted_id)
    }

# Track interaction
@app.post("/api/interactions")
def track_interaction(interaction: Interaction):
    # Validate user and product exist
    try:
        user = users_collection.find_one({"_id": ObjectId(interaction.user_id)})
        product = products_collection.find_one({"_id": ObjectId(interaction.product_id)})
        
        if not user or not product:
            raise HTTPException(status_code=404, detail="User or Product not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    interaction_doc = {
        "user_id": interaction.user_id,
        "product_id": interaction.product_id,
        "interaction_type": interaction.interaction_type,
        "rating": interaction.rating,
        "timestamp": datetime.utcnow()
    }
    
    result = interactions_collection.insert_one(interaction_doc)
    
    return {
        "message": "Interaction tracked",
        "interaction_id": str(result.inserted_id)
    }

# Get user interactions
@app.get("/api/users/{user_id}/interactions")
def get_user_interactions(user_id: str):
    interactions = list(interactions_collection.find({"user_id": user_id}))
    
    for interaction in interactions:
        interaction["_id"] = str(interaction["_id"])
    
    return {"interactions": interactions, "count": len(interactions)}

# Get product categories
@app.get("/api/categories")
def get_categories():
    categories = products_collection.distinct("category")
    return {"categories": categories}

from recommendation_routes import router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)