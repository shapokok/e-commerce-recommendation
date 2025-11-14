"""
Product routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId
import time

from app.database import (
    products_collection,
    interactions_collection,
    users_collection,
)
from app.models.schemas import Product, Interaction

router = APIRouter()


@router.get("/api/products")
def get_products(category: Optional[str] = None, search: Optional[str] = None):
    """Get all products with optional filtering"""
    start_total = time.time()

    query = {}

    if category:
        query["category"] = category

    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]

    start_query = time.time()
    products = list(products_collection.find(query).limit(50))
    query_time = (time.time() - start_query) * 1000

    print(f"[TIMING] Database query took: {query_time:.1f}ms")

    for product in products:
        product["_id"] = str(product["_id"])

    total_time = (time.time() - start_total) * 1000
    print(f"[TIMING] Total endpoint time: {total_time:.1f}ms")

    return {
        "products": products,
        "count": len(products),
        "_debug_timing": {
            "database_query_ms": round(query_time, 1),
            "total_endpoint_ms": round(total_time, 1)
        }
    }


@router.get("/api/products/{product_id}")
def get_product(product_id: str):
    """Get single product"""
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product["_id"] = str(product["_id"])
        return product
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")


@router.post("/api/products")
def create_product(product: Product):
    """Create product (for admin/testing)"""
    product_doc = product.dict()
    product_doc["created_at"] = datetime.utcnow()

    result = products_collection.insert_one(product_doc)

    return {"message": "Product created", "product_id": str(result.inserted_id)}


@router.post("/api/interactions")
def track_interaction(interaction: Interaction):
    """Track user interaction"""
    # Validate user and product exist
    try:
        user = users_collection.find_one({"_id": ObjectId(interaction.user_id)})
        product = products_collection.find_one(
            {"_id": ObjectId(interaction.product_id)}
        )

        if not user or not product:
            raise HTTPException(status_code=404, detail="User or Product not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    interaction_doc = {
        "user_id": interaction.user_id,
        "product_id": interaction.product_id,
        "interaction_type": interaction.interaction_type,
        "rating": interaction.rating,
        "timestamp": datetime.utcnow(),
    }

    result = interactions_collection.insert_one(interaction_doc)

    return {"message": "Interaction tracked", "interaction_id": str(result.inserted_id)}


@router.get("/api/categories")
def get_categories():
    """Get all product categories"""
    categories = products_collection.distinct("category")
    return {"categories": categories}

