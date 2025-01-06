from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from uuid import uuid4
from app import enums, models
from decimal import Decimal
from datetime import datetime, timezone
import random


router = APIRouter(
    tags=['Reset'],
    prefix="/reset"
)

def generate_unique_name(item_type, category, used_names):
    type_specific_names = {
        "trusou": ["Set botez", "Set nou-nascut", "Trusou spital"],
        "lumanare": ["Lumanare botez", "Lumanare aniversara"],
        "cutie": ["Cutie dar", "Cutie amintiri"],
        "accesoriu": ["Bentita", "Papucei", "Botosei"],
        "cadou": ["Set cadou", "Cos cadou"],
        "tricou": ["Tricou personalizat", "Tricou aniversar"],
        "tava": ["Tava botez", "Tava nasi"],
        "haina": ["Body", "Salopeta", "Rochita"],
        "prosop": ["Prosop botez", "Prosop personalizat"],
        "perie": ["Set perie piaptan", "Perie par bebe"],
        "oglinda": ["Oglinda personalizata", "Oglinda suvenir"]
    }
    
    base_names = type_specific_names.get(item_type, ["Produs"])
    while True:
        base_name = random.choice(base_names)
        unique_id = str(uuid4())[:8]  # Use part of a UUID to ensure uniqueness
        name = f"{base_name} {category} {unique_id}"
        if name not in used_names:
            used_names.add(name)
            return name

def generate_mock_products(db_session, count=50):
    mock_products = []
    used_names = set()
    
    for _ in range(count):
        product_type = random.choice(list(enums.ItemTypesEnum))
        categories = random.sample(list(enums.ItemCategoriesEnum), k=random.randint(1, 3))
        gender = random.choice(list(enums.GenderEnum))

        name = generate_unique_name(product_type.value, random.choice(categories).value, used_names)

        product = models.Product(
            id=str(uuid4()),
            name=name,
            item_gender=gender,
            type=product_type,
            categories=categories,
            price=Decimal(random.uniform(10, 500)).quantize(Decimal("0.01")),
            primary_image=f"https://example.com/images/{uuid4()}.jpg",
            secondary_images=[f"https://example.com/images/{uuid4()}.jpg" for _ in range(random.randint(0, 3))],
            created_at=datetime.now(timezone.utc)
        )
        
        mock_products.append(product)
    
    return mock_products

@router.get("")
def reset_products(db: Session = Depends(get_db)):
    try:
        # Step 1: Delete all existing entries in the carts table
        db.query(models.Cart).delete()
        
        # Step 2: Delete all existing products
        db.query(models.Product).delete()
        
        # Step 3: Generate new mock products
        new_products = generate_mock_products(db, count=500)
        
        # Step 4: Add new products to the session
        db.add_all(new_products)
        
        # Commit the changes
        db.commit()
        
        return {
            "message": "Products and carts have been reset successfully",
            "new_product_count": len(new_products)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")