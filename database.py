"""
Shared MongoDB connection for the entire application.
This ensures we use a single connection pool across all modules.
"""
from pymongo import MongoClient
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("[OPTIMIZATION] Initializing shared MongoDB connection with connection pooling...")

MONGO_URI = "mongodb://127.0.0.1:27017/"  # Local MongoDB
print(f"[DEBUG] MONGO_URI = {MONGO_URI}")

# Create single MongoDB client with connection pooling
client = MongoClient(
    MONGO_URI,
    maxPoolSize=50,  # Maximum number of connections in the pool
    minPoolSize=10,  # Minimum number of connections to keep open
    maxIdleTimeMS=45000,  # Close connections after 45s of inactivity
    serverSelectionTimeoutMS=5000,  # Timeout for selecting a server
    connectTimeoutMS=10000,  # Timeout for initial connection
)

# Database instance
db = client.ecommerce_db

# Collections
users_collection = db.users
products_collection = db.products
interactions_collection = db.interactions
carts_collection = db.carts
orders_collection = db.orders
password_reset_tokens = db.password_reset_tokens

print("[OPTIMIZATION] MongoDB client configured with connection pooling (maxPoolSize=50)")
print(f"[DEBUG] Connected to: {client.address}")
print("[OPTIMIZATION] All collections initialized")
