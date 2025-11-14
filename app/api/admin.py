"""
Admin routes
"""
from fastapi import APIRouter, HTTPException
from bson import ObjectId

from app.database import (
    users_collection,
    products_collection,
    orders_collection,
)
from app.models.schemas import ProductUpdate

router = APIRouter()


@router.get("/api/admin/stats")
def get_admin_stats(admin_user_id: str):
    """Get admin dashboard statistics"""
    try:
        # Check admin permissions
        admin = users_collection.find_one({"_id": ObjectId(admin_user_id)})
        if not admin or not admin.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")

        total_users = users_collection.count_documents({})
        total_products = products_collection.count_documents({})
        total_orders = orders_collection.count_documents({})
        total_revenue = 0

        # Calculate revenue
        orders = orders_collection.find({"status": {"$ne": "cancelled"}})
        for order in orders:
            total_revenue += order.get("total", 0)

        # Popular categories
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]
        popular_categories = list(products_collection.aggregate(pipeline))

        # Low stock products
        low_stock_products = list(
            products_collection.find({"stock_quantity": {"$lt": 10}}).limit(10)
        )

        for product in low_stock_products:
            product["_id"] = str(product["_id"])

        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "popular_categories": popular_categories,
            "low_stock_products": low_stock_products,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/admin/orders")
def get_all_orders(admin_user_id: str):
    """Get all orders (admin only)"""
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


@router.put("/api/admin/products/{product_id}")
def update_product(admin_user_id: str, product_id: str, update: ProductUpdate):
    """Update product (admin only)"""
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
                {"_id": ObjectId(product_id)}, {"$set": update_fields}
            )

        return {"message": "Product updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/admin/products/{product_id}")
def delete_product(admin_user_id: str, product_id: str):
    """Delete product (admin only)"""
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

