from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from .enums import GenderEnum, ItemTypesEnum, ItemCategoriesEnum
import re

class userLogin(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    email: EmailStr
    surname: str
    name: str
    gender: GenderEnum

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str
    @field_validator('password')
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
class UserResponse(UserBase):
    role: str

    class Config:
        from_attributes = True
    
class ProductBase(BaseModel):
    id: str
    name: str
    item_gender: GenderEnum
    categories: Optional[List[ItemCategoriesEnum]] = None
    type: ItemTypesEnum
    price: float

class ProductResponse(ProductBase):
    rating: float
    primary_image: Optional[str] = None
    secondary_images: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QueryResponse(BaseModel):
    items: List[ProductResponse]
    count: int

class SetBase(BaseModel):
    set_name: str
    set_items: List[str]

class CartItemBase(BaseModel):
    _user_id: int
    product_id: str
    quantity: int

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    product_id: str
    user_id: int
    message: Optional[str]
    stars: int

class ReviewResponse(ReviewBase):
    created_at: datetime

    class Config:
        from_attributes = True
