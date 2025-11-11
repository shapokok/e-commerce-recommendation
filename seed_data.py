from pymongo import MongoClient
import bcrypt
from datetime import datetime
import random

MONGO_URI = "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.ecommerce_db

users_collection = db.users
products_collection = db.products
interactions_collection = db.interactions

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def clear_database():
    """Clear all collections"""
    print("Clearing database...")
    users_collection.delete_many({})
    products_collection.delete_many({})
    interactions_collection.delete_many({})
    print("Database cleared!")

def seed_users():
    """Create test users"""
    print("Creating users...")
    
    users = [
        {"username": "alice", "email": "alice@example.com", "password": "password123", "preferences": ["Electronics", "Books"]},
        {"username": "bob", "email": "bob@example.com", "password": "password123", "preferences": ["Clothing", "Sports"]},
        {"username": "charlie", "email": "charlie@example.com", "password": "password123", "preferences": ["Home & Garden", "Electronics"]},
        {"username": "diana", "email": "diana@example.com", "password": "password123", "preferences": ["Beauty", "Clothing"]},
        {"username": "eve", "email": "eve@example.com", "password": "password123", "preferences": ["Books", "Toys"]},
        {"username": "frank", "email": "frank@example.com", "password": "password123", "preferences": ["Sports", "Electronics"]},
        {"username": "grace", "email": "grace@example.com", "password": "password123", "preferences": ["Beauty", "Home & Garden"]},
        {"username": "henry", "email": "henry@example.com", "password": "password123", "preferences": ["Electronics", "Sports"]},
    ]
    
    user_ids = []
    for user in users:
        user_doc = {
            "username": user["username"],
            "email": user["email"],
            "password_hash": hash_password(user["password"]),
            "preferences": user["preferences"],
            "created_at": datetime.utcnow()
        }
        result = users_collection.insert_one(user_doc)
        user_ids.append(str(result.inserted_id))
        print(f"Created user: {user['username']} (ID: {result.inserted_id})")
    
    return user_ids

def seed_products():
    """Create test products with stock"""
    print("\nCreating products...")
    
    products = [
        # Electronics
        {"name": "Laptop Pro 15", "description": "High-performance laptop for professionals", "category": "Electronics", "price": 1299.99, "stock_quantity": 15, "image_url": "https://via.placeholder.com/300x300?text=Laptop"},
        {"name": "Smartphone X", "description": "Latest smartphone with amazing camera", "category": "Electronics", "price": 899.99, "stock_quantity": 25, "image_url": "https://via.placeholder.com/300x300?text=Phone"},
        {"name": "Wireless Headphones", "description": "Noise-cancelling wireless headphones", "category": "Electronics", "price": 249.99, "stock_quantity": 50, "image_url": "https://via.placeholder.com/300x300?text=Headphones"},
        {"name": "Smart Watch", "description": "Fitness tracking smartwatch", "category": "Electronics", "price": 399.99, "stock_quantity": 30, "image_url": "https://via.placeholder.com/300x300?text=Watch"},
        {"name": "Tablet 10\"", "description": "Portable tablet for work and play", "category": "Electronics", "price": 499.99, "stock_quantity": 20, "image_url": "https://via.placeholder.com/300x300?text=Tablet"},
        
        # Books
        {"name": "Python Programming Guide", "description": "Complete guide to Python programming", "category": "Books", "price": 49.99, "stock_quantity": 100, "image_url": "https://via.placeholder.com/300x300?text=Python+Book"},
        {"name": "Data Science Handbook", "description": "Master data science techniques", "category": "Books", "price": 59.99, "stock_quantity": 75, "image_url": "https://via.placeholder.com/300x300?text=Data+Science"},
        {"name": "Machine Learning Basics", "description": "Introduction to ML algorithms", "category": "Books", "price": 44.99, "stock_quantity": 80, "image_url": "https://via.placeholder.com/300x300?text=ML+Book"},
        {"name": "Web Development 101", "description": "Learn modern web development", "category": "Books", "price": 39.99, "stock_quantity": 90, "image_url": "https://via.placeholder.com/300x300?text=Web+Dev"},
        
        # Clothing
        {"name": "Cotton T-Shirt", "description": "Comfortable cotton t-shirt", "category": "Clothing", "price": 24.99, "stock_quantity": 200, "image_url": "https://via.placeholder.com/300x300?text=T-Shirt"},
        {"name": "Denim Jeans", "description": "Classic blue denim jeans", "category": "Clothing", "price": 59.99, "stock_quantity": 150, "image_url": "https://via.placeholder.com/300x300?text=Jeans"},
        {"name": "Winter Jacket", "description": "Warm winter jacket", "category": "Clothing", "price": 129.99, "stock_quantity": 40, "image_url": "https://via.placeholder.com/300x300?text=Jacket"},
        {"name": "Running Shoes", "description": "Lightweight running shoes", "category": "Clothing", "price": 89.99, "stock_quantity": 60, "image_url": "https://via.placeholder.com/300x300?text=Shoes"},
        
        # Sports
        {"name": "Yoga Mat", "description": "Non-slip yoga mat", "category": "Sports", "price": 29.99, "stock_quantity": 100, "image_url": "https://via.placeholder.com/300x300?text=Yoga+Mat"},
        {"name": "Dumbbell Set", "description": "Adjustable dumbbell set", "category": "Sports", "price": 149.99, "stock_quantity": 35, "image_url": "https://via.placeholder.com/300x300?text=Dumbbells"},
        {"name": "Basketball", "description": "Official size basketball", "category": "Sports", "price": 34.99, "stock_quantity": 75, "image_url": "https://via.placeholder.com/300x300?text=Basketball"},
        {"name": "Tennis Racket", "description": "Professional tennis racket", "category": "Sports", "price": 119.99, "stock_quantity": 25, "image_url": "https://via.placeholder.com/300x300?text=Racket"},
        
        # Home & Garden
        {"name": "Coffee Maker", "description": "Automatic coffee maker", "category": "Home & Garden", "price": 79.99, "stock_quantity": 45, "image_url": "https://via.placeholder.com/300x300?text=Coffee"},
        {"name": "Plant Pot Set", "description": "Set of ceramic plant pots", "category": "Home & Garden", "price": 39.99, "stock_quantity": 80, "image_url": "https://via.placeholder.com/300x300?text=Pots"},
        {"name": "LED Desk Lamp", "description": "Adjustable LED desk lamp", "category": "Home & Garden", "price": 49.99, "stock_quantity": 55, "image_url": "https://via.placeholder.com/300x300?text=Lamp"},
        
        # Beauty
        {"name": "Facial Cream", "description": "Moisturizing facial cream", "category": "Beauty", "price": 34.99, "stock_quantity": 120, "image_url": "https://via.placeholder.com/300x300?text=Cream"},
        {"name": "Makeup Kit", "description": "Complete makeup kit", "category": "Beauty", "price": 89.99, "stock_quantity": 40, "image_url": "https://via.placeholder.com/300x300?text=Makeup"},
        {"name": "Hair Dryer", "description": "Professional hair dryer", "category": "Beauty", "price": 69.99, "stock_quantity": 30, "image_url": "https://via.placeholder.com/300x300?text=Dryer"},
        
        # Toys
        {"name": "Building Blocks Set", "description": "Creative building blocks", "category": "Toys", "price": 44.99, "stock_quantity": 65, "image_url": "https://via.placeholder.com/300x300?text=Blocks"},
        {"name": "Board Game Collection", "description": "Family board game", "category": "Toys", "price": 29.99, "stock_quantity": 90, "image_url": "https://via.placeholder.com/300x300?text=Game"},
    ]
    
    product_ids = []
    for product in products:
        product["created_at"] = datetime.utcnow()
        result = products_collection.insert_one(product)
        product_ids.append(str(result.inserted_id))
        print(f"Created product: {product['name']} (Stock: {product['stock_quantity']}) (ID: {result.inserted_id})")
    
    return product_ids

#функция для создания админа
def seed_admin():
    """Create admin user"""
    print("\nCreating admin user...")
    
    admin = {
        "username": "admin",
        "email": "admin@eshop.com",
        "password_hash": hash_password("admin123"),
        "preferences": [],
        "is_admin": True,
        "created_at": datetime.utcnow()
    }
    
    # Проверить, есть ли уже админ
    existing = users_collection.find_one({"email": "admin@eshop.com"})
    if existing:
        print("Admin already exists")
        return str(existing["_id"])
    
    result = users_collection.insert_one(admin)
    print(f"Created admin: {admin['username']} (ID: {result.inserted_id})")
    print("Admin credentials: admin@eshop.com / admin123")
    
    return str(result.inserted_id)

def seed_interactions(user_ids, product_ids):
    """Create realistic interactions"""
    print("\nCreating interactions...")
    
    interaction_types = ["view", "like", "rating"]
    
    # Create realistic interaction patterns
    interactions_count = 0
    
    for user_id in user_ids:
        # Each user interacts with 5-15 random products
        num_interactions = random.randint(5, 15)
        selected_products = random.sample(product_ids, num_interactions)
        
        for product_id in selected_products:
            # Varying interaction types
            interaction_type = random.choice(interaction_types)
            
            interaction = {
                "user_id": user_id,
                "product_id": product_id,
                "interaction_type": interaction_type,
                "timestamp": datetime.utcnow()
            }
            
            if interaction_type == "rating":
                interaction["rating"] = random.randint(1, 5)
            else:
                interaction["rating"] = None
            
            interactions_collection.insert_one(interaction)
            interactions_count += 1
    
    print(f"Created {interactions_count} interactions")

def main():
    print("=" * 50)
    print("Seeding Database with Test Data")
    print("=" * 50)
    
    # Clear existing data
    clear_database()
    
    # Seed data
    seed_admin()  # ← ДОБАВИТЬ ЭТУ СТРОКУ
    user_ids = seed_users()
    product_ids = seed_products()
    seed_interactions(user_ids, product_ids)
    
    print("\n" + "=" * 50)
    print("Database seeding completed!")
    print("=" * 50)
    print(f"\nCreated:")
    print(f"- 1 admin user")  # ← ОБНОВИТЬ
    print(f"- {len(user_ids)} regular users")
    print(f"- {len(product_ids)} products with stock")
    print(f"- Multiple interactions")
    print("\nTest credentials:")
    print("Admin: admin@eshop.com / admin123")  # ← ДОБАВИТЬ
    print("User: alice@example.com / password123")
    print("User: bob@example.com / password123")
    print("\nYou can now start the API server!")

if __name__ == "__main__":
    main()