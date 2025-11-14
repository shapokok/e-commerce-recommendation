"""
API routes package
"""
from app.api import auth, users, products, cart, orders, admin, recommendations

__all__ = ["auth", "users", "products", "cart", "orders", "admin", "recommendations"]
