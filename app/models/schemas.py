"""
Pydantic models and schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List


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


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None


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

