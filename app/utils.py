from passlib.context import CryptContext
import random
from datetime import datetime, timezone
from uuid import uuid4
from decimal import Decimal
from .models import Product
from .enums import ItemTypesEnum, ItemCategoriesEnum, GenderEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify_hash(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)