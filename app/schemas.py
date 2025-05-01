from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, Json
from datetime import datetime
from .enums import GenderEnum, ItemTypesEnum, ItemCategoriesEnum
import re

'''BEGIN-COOKIES'''

class Cookies(BaseModel):
    authToken: str | None = None
    guestSessionToken: str | None = None

'''END-COOKIES'''

''''BEGIN-USER'''

class UserLogin(BaseModel):
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

''''END-USER'''
    
''''BEGIN-PRODUCT'''

class ProductBase(BaseModel):
    id: str
    name: str
    item_gender: GenderEnum
    categories: Optional[List[ItemCategoriesEnum]] = None
    type: ItemTypesEnum
    price: float

class ProductSet(BaseModel):
    set_type: str
    primary_product_ids: List[str]
    secondary_product_ids: Optional[List[str]] = None

class ProductResponse(ProductBase):
    rating: Optional[float]
    primary_image: Optional[str] = None
    secondary_images: Optional[List[str]] = None
    product_set: Optional[ProductSet] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SetBase(BaseModel):
    id: str
    set_type: str
    primary_product_ids: List[str]
    secondary_product_ids: Optional[List[str]] = None

''''END-PRODUCT'''

''''BEGIN-QUERY'''

class QueryResponse(BaseModel):
    items: List[ProductResponse]
    count: int

''''END-QUERY'''

class CartItemBase(BaseModel):
    _user_id: int
    product_id: str
    quantity: int
    product_name: str
    product_type: str
    product_price: float
    product_primary_image: str
    personalised_fields: Optional[Json] = None

    class Config:
        from_attributes = True

class CartItemResponse(CartItemBase):
    id: int

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    product_id: str
    user_id: int
    message: Optional[str]
    stars: int

class ReviewResponse(ReviewBase):
    created_at: datetime
    author_surname: str
    author_name: str

    class Config:
        from_attributes = True
