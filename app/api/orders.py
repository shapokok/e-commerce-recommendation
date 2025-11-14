"""
Order routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId

from app.database import (
    orders_collection,
    carts_collection,
    products_collection,
)
from app.models.schemas import CheckoutRequest

router = APIRouter()


@router.post("/api/checkout/{user_id}")
def checkout(user_id: str, checkout_data: CheckoutRequest):
    """Checkout and create order from cart"""
    try:
        # Get cart
        cart = carts_collection.find_one({"user_id": user_id})
        if not cart or not cart.get("items"):
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Check stock and update
        order_items = []
        total = 0

        for item in cart["items"]:
            product = products_collection.find_one(
                {"_id": ObjectId(item["product_id"])}
            )
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product {item['product_id']} not found"
                )

            stock = product.get("stock_quantity", 0)
            if stock < item["quantity"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {product['name']}. Available: {stock}",
                )

            # Decrease stock
            new_stock = stock - item["quantity"]
            products_collection.update_one(
                {"_id": ObjectId(item["product_id"])},
                {"$set": {"stock_quantity": new_stock}},
            )

            # Add to order
            subtotal = product["price"] * item["quantity"]
            total += subtotal

            order_items.append(
                {
                    "product_id": item["product_id"],
                    "product_name": product["name"],
                    "price": product["price"],
                    "quantity": item["quantity"],
                    "subtotal": subtotal,
                }
            )

        # Create order
        order = {
            "user_id": user_id,
            "items": order_items,
            "total": round(total, 2),
            "shipping_address": checkout_data.shipping_address,
            "payment_method": checkout_data.payment_method,
            "status": "confirmed",  # confirmed, shipped, delivered, cancelled
            "created_at": datetime.utcnow(),
        }

        result = orders_collection.insert_one(order)

        # Clear cart
        carts_collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [], "updated_at": datetime.utcnow()}},
        )

        return {
            "message": "Order placed successfully",
            "order_id": str(result.inserted_id),
            "total": order["total"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/orders/{user_id}")
def get_user_orders(user_id: str):
    """Get all orders for a user"""
    try:
        orders = list(
            orders_collection.find({"user_id": user_id}).sort("created_at", -1)
        )

        for order in orders:
            order["_id"] = str(order["_id"])

        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/orders/detail/{order_id}")
def get_order_detail(order_id: str):
    """Get order details"""
    try:
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        order["_id"] = str(order["_id"])
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid order ID")

