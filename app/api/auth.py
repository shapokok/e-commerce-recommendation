"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from bson import ObjectId

from app.database import (
    users_collection,
    password_reset_tokens,
)
from app.models.schemas import (
    UserRegister,
    UserLogin,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.auth import (
    hash_password,
    verify_password,
    generate_reset_token,
    send_reset_email,
)

router = APIRouter()


@router.post("/api/register")
def register_user(user: UserRegister):
    """Register a new user"""
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
        "created_at": datetime.utcnow(),
    }

    result = users_collection.insert_one(user_doc)

    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
        "username": user.username,
    }


@router.post("/api/login")
def login_user(credentials: UserLogin):
    """User login"""
    user = users_collection.find_one({"email": credentials.email})

    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "username": user["username"],
        "is_admin": user.get("is_admin", False),
    }


@router.post("/api/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    """Request password reset"""
    try:
        user = users_collection.find_one({"email": request.email})
        if not user:
            # Security: don't reveal if email exists
            return {"message": "If the email exists, a reset link has been sent"}

        # Create token
        token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Save token
        password_reset_tokens.insert_one(
            {
                "user_id": str(user["_id"]),
                "token": token,
                "expires_at": expires_at,
                "used": False,
            }
        )

        # Send email
        send_reset_email(request.email, token)

        return {"message": "If the email exists, a reset link has been sent"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/reset-password")
def reset_password(request: ResetPasswordRequest):
    """Reset password with token"""
    try:
        # Find token
        token_doc = password_reset_tokens.find_one(
            {"token": request.token, "used": False}
        )

        if not token_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        # Check expiration
        if datetime.utcnow() > token_doc["expires_at"]:
            raise HTTPException(status_code=400, detail="Token has expired")

        # Update password
        new_hash = hash_password(request.new_password)
        users_collection.update_one(
            {"_id": ObjectId(token_doc["user_id"])},
            {"$set": {"password_hash": new_hash}},
        )

        # Mark token as used
        password_reset_tokens.update_one(
            {"_id": token_doc["_id"]}, {"$set": {"used": True}}
        )

        return {"message": "Password has been reset successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

