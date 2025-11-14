"""
Shopping cart routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId

from app.database import (
    carts_collection,
    products_collection,
)
from app.models.schemas import CartItem, UpdateCartItem

router = APIRouter()


@router.get("/api/cart/{user_id}")
def get_cart(user_id: str):
    """Get user's cart"""
    try:
        cart = carts_collection.find_one({"user_id": user_id})

        if not cart:
            return {"user_id": user_id, "items": [], "total": 0}

        # Enrich with product details
        enriched_items = []
        total = 0

        for item in cart.get("items", []):
            try:
                product = products_collection.find_one(
                    {"_id": ObjectId(item["product_id"])}
                )
                if product:
                    product_data = {
                        "_id": str(product["_id"]),
                        "name": product["name"],
                        "price": product["price"],
                        "image_url": product.get("image_url", ""),
                        "stock_quantity": product.get("stock_quantity", 0),
                        "quantity": item["quantity"],
                        "subtotal": product["price"] * item["quantity"],
                    }
                    enriched_items.append(product_data)
                    total += product_data["subtotal"]
            except:
                continue

        return {"user_id": user_id, "items": enriched_items, "total": round(total, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/cart/{user_id}/items")
def add_to_cart(user_id: str, item: CartItem):
    """Add item to cart"""
    try:
        # Check product and stock
        product = products_collection.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        stock = product.get("stock_quantity", 0)
        if stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Only {stock} items in stock")

        # Find or create cart
        cart = carts_collection.find_one({"user_id": user_id})

        if not cart:
            # Create new cart
            carts_collection.insert_one(
                {
                    "user_id": user_id,
                    "items": [
                        {"product_id": item.product_id, "quantity": item.quantity}
                    ],
                    "updated_at": datetime.utcnow(),
                }
            )
        else:
            # Update existing cart
            items = cart.get("items", [])
            found = False

            for cart_item in items:
                if cart_item["product_id"] == item.product_id:
                    new_quantity = cart_item["quantity"] + item.quantity
                    if new_quantity > stock:
                        raise HTTPException(
                            status_code=400, detail=f"Only {stock} items in stock"
                        )
                    cart_item["quantity"] = new_quantity
                    found = True
                    break

            if not found:
                items.append({"product_id": item.product_id, "quantity": item.quantity})

            carts_collection.update_one(
                {"user_id": user_id},
                {"$set": {"items": items, "updated_at": datetime.utcnow()}},
            )

        return {"message": "Item added to cart", "product_id": item.product_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/cart/{user_id}/items/{product_id}")
def update_cart_item(user_id: str, product_id: str, update: UpdateCartItem):
    """Update cart item quantity"""
    try:
        # Check stock
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        stock = product.get("stock_quantity", 0)
        if update.quantity > stock:
            raise HTTPException(status_code=400, detail=f"Only {stock} items in stock")

        if update.quantity <= 0:
            # Remove from cart
            carts_collection.update_one(
                {"user_id": user_id}, {"$pull": {"items": {"product_id": product_id}}}
            )
            return {"message": "Item removed from cart"}

        # Update quantity
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
            {"$set": {"items": items, "updated_at": datetime.utcnow()}},
        )

        return {"message": "Cart updated", "quantity": update.quantity}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/cart/{user_id}/items/{product_id}")
def remove_from_cart(user_id: str, product_id: str):
    """Remove item from cart"""
    try:
        carts_collection.update_one(
            {"user_id": user_id}, {"$pull": {"items": {"product_id": product_id}}}
        )
        return {"message": "Item removed from cart"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/cart/{user_id}")
def clear_cart(user_id: str):
    """Clear entire cart"""
    try:
        carts_collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [], "updated_at": datetime.utcnow()}},
        )
        return {"message": "Cart cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

