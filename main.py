from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import bcrypt
from pymongo import MongoClient
from bson import ObjectId
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# MongoDB connection
MONGO_URI = "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.ecommerce_db

# Collections
users_collection = db.users
products_collection = db.products
interactions_collection = db.interactions
carts_collection = db.carts
orders_collection = db.orders
password_reset_tokens = db.password_reset_tokens

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

class CartItem(BaseModel):
    product_id: str
    quantity: int

class UpdateCartItem(BaseModel):
    quantity: int

class CheckoutRequest(BaseModel):
    shipping_address: str
    payment_method: str  # "credit_card", "paypal", etc.

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None

# Helper function
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def send_reset_email(email: str, token: str):
    """Симуляция отправки email"""
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    print(f"\n{'='*60}")
    print(f"PASSWORD RESET EMAIL")
    print(f"To: {email}")
    print(f"Reset Link: {reset_link}")
    print(f"Token: {token}")
    print(f"{'='*60}\n")
    # В продакшене используйте SMTP для реальной отправки

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

# ==================== SHOPPING CART ====================

@app.get("/api/cart/{user_id}")
def get_cart(user_id: str):
    """Получить корзину пользователя"""
    try:
        cart = carts_collection.find_one({"user_id": user_id})
        
        if not cart:
            return {"user_id": user_id, "items": [], "total": 0}
        
        # Обогатить данными о продуктах
        enriched_items = []
        total = 0
        
        for item in cart.get("items", []):
            try:
                product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
                if product:
                    product_data = {
                        "_id": str(product["_id"]),
                        "name": product["name"],
                        "price": product["price"],
                        "image_url": product.get("image_url", ""),
                        "stock_quantity": product.get("stock_quantity", 0),
                        "quantity": item["quantity"],
                        "subtotal": product["price"] * item["quantity"]
                    }
                    enriched_items.append(product_data)
                    total += product_data["subtotal"]
            except:
                continue
        
        return {
            "user_id": user_id,
            "items": enriched_items,
            "total": round(total, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cart/{user_id}/items")
def add_to_cart(user_id: str, item: CartItem):
    """Добавить товар в корзину"""
    try:
        # Проверить наличие товара и stock
        product = products_collection.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        stock = product.get("stock_quantity", 0)
        if stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Only {stock} items in stock")
        
        # Найти или создать корзину
        cart = carts_collection.find_one({"user_id": user_id})
        
        if not cart:
            # Создать новую корзину
            carts_collection.insert_one({
                "user_id": user_id,
                "items": [{"product_id": item.product_id, "quantity": item.quantity}],
                "updated_at": datetime.utcnow()
            })
        else:
            # Обновить существующую корзину
            items = cart.get("items", [])
            found = False
            
            for cart_item in items:
                if cart_item["product_id"] == item.product_id:
                    new_quantity = cart_item["quantity"] + item.quantity
                    if new_quantity > stock:
                        raise HTTPException(status_code=400, detail=f"Only {stock} items in stock")
                    cart_item["quantity"] = new_quantity
                    found = True
                    break
            
            if not found:
                items.append({"product_id": item.product_id, "quantity": item.quantity})
            
            carts_collection.update_one(
                {"user_id": user_id},
                {"$set": {"items": items, "updated_at": datetime.utcnow()}}
            )
        
        return {"message": "Item added to cart", "product_id": item.product_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/cart/{user_id}/items/{product_id}")
def update_cart_item(user_id: str, product_id: str, update: UpdateCartItem):
    """Обновить количество товара в корзине"""
    try:
        # Проверить stock
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        stock = product.get("stock_quantity", 0)
        if update.quantity > stock:
            raise HTTPException(status_code=400, detail=f"Only {stock} items in stock")
        
        if update.quantity <= 0:
            # Удалить из корзины
            carts_collection.update_one(
                {"user_id": user_id},
                {"$pull": {"items": {"product_id": product_id}}}
            )
            return {"message": "Item removed from cart"}
        
        # Обновить количество
        cart = carts_collection.find_one({"user_id": user_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        items = cart.get("items", [])
        for item in items:
            if item["product_id"] == product_id:
                item["quantity"] = update.quantity
                break
        
        carts_collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Cart updated", "quantity": update.quantity}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cart/{user_id}/items/{product_id}")
def remove_from_cart(user_id: str, product_id: str):
    """Удалить товар из корзины"""
    try:
        carts_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"items": {"product_id": product_id}}}
        )
        return {"message": "Item removed from cart"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cart/{user_id}")
def clear_cart(user_id: str):
    """Очистить всю корзину"""
    try:
        carts_collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [], "updated_at": datetime.utcnow()}}
        )
        return {"message": "Cart cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CHECKOUT ====================

@app.post("/api/checkout/{user_id}")
def checkout(user_id: str, checkout_data: CheckoutRequest):
    """Оформить заказ из корзины"""
    try:
        # Получить корзину
        cart = carts_collection.find_one({"user_id": user_id})
        if not cart or not cart.get("items"):
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Проверить наличие и обновить stock
        order_items = []
        total = 0
        
        for item in cart["items"]:
            product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
            
            stock = product.get("stock_quantity", 0)
            if stock < item["quantity"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough stock for {product['name']}. Available: {stock}"
                )
            
            # Уменьшить stock
            new_stock = stock - item["quantity"]
            products_collection.update_one(
                {"_id": ObjectId(item["product_id"])},
                {"$set": {"stock_quantity": new_stock}}
            )
            
            # Добавить в заказ
            subtotal = product["price"] * item["quantity"]
            total += subtotal
            
            order_items.append({
                "product_id": item["product_id"],
                "product_name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"],
                "subtotal": subtotal
            })
        
        # Создать заказ
        order = {
            "user_id": user_id,
            "items": order_items,
            "total": round(total, 2),
            "shipping_address": checkout_data.shipping_address,
            "payment_method": checkout_data.payment_method,
            "status": "confirmed",  # confirmed, shipped, delivered, cancelled
            "created_at": datetime.utcnow()
        }
        
        result = orders_collection.insert_one(order)
        
        # Очистить корзину
        carts_collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [], "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": "Order placed successfully",
            "order_id": str(result.inserted_id),
            "total": order["total"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{user_id}")
def get_user_orders(user_id: str):
    """Получить все заказы пользователя"""
    try:
        orders = list(orders_collection.find({"user_id": user_id}).sort("created_at", -1))
        
        for order in orders:
            order["_id"] = str(order["_id"])
        
        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/detail/{order_id}")
def get_order_detail(order_id: str):
    """Получить детали заказа"""
    try:
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order["_id"] = str(order["_id"])
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid order ID")

# ==================== PASSWORD RESET ====================

@app.post("/api/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    """Запрос на восстановление пароля"""
    try:
        user = users_collection.find_one({"email": request.email})
        if not user:
            # В целях безопасности не говорим, существует ли email
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Создать токен
        token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Токен действует 1 час
        
        # Сохранить токен
        password_reset_tokens.insert_one({
            "user_id": str(user["_id"]),
            "token": token,
            "expires_at": expires_at,
            "used": False
        })
        
        # Отправить email
        send_reset_email(request.email, token)
        
        return {"message": "If the email exists, a reset link has been sent"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset-password")
def reset_password(request: ResetPasswordRequest):
    """Сбросить пароль с токеном"""
    try:
        # Найти токен
        token_doc = password_reset_tokens.find_one({
            "token": request.token,
            "used": False
        })
        
        if not token_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        # Проверить срок действия
        if datetime.utcnow() > token_doc["expires_at"]:
            raise HTTPException(status_code=400, detail="Token has expired")
        
        # Обновить пароль
        new_hash = hash_password(request.new_password)
        users_collection.update_one(
            {"_id": ObjectId(token_doc["user_id"])},
            {"$set": {"password_hash": new_hash}}
        )
        
        # Отметить токен как использованный
        password_reset_tokens.update_one(
            {"_id": token_doc["_id"]},
            {"$set": {"used": True}}
        )
        
        return {"message": "Password has been reset successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN ROUTES ====================

@app.get("/api/admin/stats")
def get_admin_stats(admin_user_id: str):
    """Получить статистику для админ-панели"""
    try:
        # Проверить права админа
        admin = users_collection.find_one({"_id": ObjectId(admin_user_id)})
        if not admin or not admin.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        total_users = users_collection.count_documents({})
        total_products = products_collection.count_documents({})
        total_orders = orders_collection.count_documents({})
        total_revenue = 0
        
        # Подсчитать выручку
        orders = orders_collection.find({"status": {"$ne": "cancelled"}})
        for order in orders:
            total_revenue += order.get("total", 0)
        
        # Популярные категории
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        popular_categories = list(products_collection.aggregate(pipeline))
        
        # Продукты с низким stock
        low_stock_products = list(products_collection.find(
            {"stock_quantity": {"$lt": 10}}
        ).limit(10))
        
        for product in low_stock_products:
            product["_id"] = str(product["_id"])
        
        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "popular_categories": popular_categories,
            "low_stock_products": low_stock_products
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/orders")
def get_all_orders(admin_user_id: str):
    """Получить все заказы (только для админа)"""
    try:
        admin = users_collection.find_one({"_id": ObjectId(admin_user_id)})
        if not admin or not admin.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        orders = list(orders_collection.find().sort("created_at", -1).limit(50))
        
        for order in orders:
            order["_id"] = str(order["_id"])
        
        return {"orders": orders, "count": len(orders)}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/products/{product_id}")
def update_product(admin_user_id: str, product_id: str, update: ProductUpdate):
    """Обновить продукт (только для админа)"""
    try:
        admin = users_collection.find_one({"_id": ObjectId(admin_user_id)})
        if not admin or not admin.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        update_fields = {}
        if update.name is not None:
            update_fields["name"] = update.name
        if update.description is not None:
            update_fields["description"] = update.description
        if update.category is not None:
            update_fields["category"] = update.category
        if update.price is not None:
            update_fields["price"] = update.price
        if update.stock_quantity is not None:
            update_fields["stock_quantity"] = update.stock_quantity
        if update.image_url is not None:
            update_fields["image_url"] = update.image_url
        
        if update_fields:
            products_collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_fields}
            )
        
        return {"message": "Product updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/products/{product_id}")
def delete_product(admin_user_id: str, product_id: str):
    """Удалить продукт (только для админа)"""
    try:
        admin = users_collection.find_one({"_id": ObjectId(admin_user_id)})
        if not admin or not admin.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        products_collection.delete_one({"_id": ObjectId(product_id)})
        
        return {"message": "Product deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================================
# КОНЕЦ НОВЫХ ЭНДПОИНТОВ
# ===================================================================

from recommendation_routes import router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)