"""
User management routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.database import (
    users_collection,
    interactions_collection,
    products_collection,
)
from app.models.schemas import UserUpdate

router = APIRouter()


@router.get("/api/users/{user_id}")
def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.put("/api/users/{user_id}")
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
            existing = users_collection.find_one(
                {"username": update_data.username, "_id": {"$ne": ObjectId(user_id)}}
            )
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
                {"_id": ObjectId(user_id)}, {"$set": update_fields}
            )

        # Return updated user
        updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
        updated_user["_id"] = str(updated_user["_id"])
        updated_user.pop("password_hash", None)

        return {"message": "Profile updated successfully", "user": updated_user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.get("/api/users/{user_id}/history")
def get_user_history(user_id: str, interaction_type: Optional[str] = None):
    """Get user's interaction history with product details"""
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
                product = products_collection.find_one(
                    {"_id": ObjectId(interaction["product_id"])}
                )
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
                            "image_url": product.get("image_url", ""),
                        },
                    }
                    history.append(history_item)
            except:
                continue

        return {"user_id": user_id, "history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/users/{user_id}/interactions")
def get_user_interactions(user_id: str):
    """Get user interactions"""
    interactions = list(interactions_collection.find({"user_id": user_id}))

    for interaction in interactions:
        interaction["_id"] = str(interaction["_id"])

    return {"interactions": interactions, "count": len(interactions)}

