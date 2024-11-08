from typing import Optional

from sqlalchemy import func
from app.database import get_db
from app import models, oauth2, schemas, enums
from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from typing import List
import os
import shutil

router = APIRouter(
    tags=['Products'],
    prefix="/products"
)

@router.get("", response_model=schemas.QueryResponse)
def get_products(categories: Optional[str] = Query(None), search: Optional[str] = Query(None), type: Optional[str] = Query(None), gender: Optional[str] = Query(None), skip: int = Query(default=0, ge=0),  limit: int = 16, db: Session = Depends(get_db)):
    query = db.query(models.Product)

    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))

    if categories:
        categories = (categories.split("+"))
        query = query.filter(models.Product.categories.contains([categories]))

    if type:
        try: 
            type = enums.ItemTypesEnum[type]
            query = query.filter(models.Product.type == type)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Tipul de produs {type} nu exista')

    if gender:
        gender_map = {"fete": "F", "baieti": "M"}
        gender_value = gender_map.get(gender, "U")
        query = query.filter(models.Product.item_gender == gender_value)

    count = query.with_entities(func.count()).scalar()
    products = query.offset(skip * limit).limit(limit).all()

    return {"items": products, "count": count}

@router.get("/{id}")
def get_product(id: str, db: Session = Depends(get_db)):
    found_post = db.query(models.Product).filter(models.Product.id == id).first()

    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Produsul cu id-ul {id} nu exista!')
    
    return found_post

@router.get("/{id}/reviews", response_model=List[schemas.ReviewResponse])
def get_product_reviews(id: str, db: Session = Depends(get_db)):
    found_post = db.query(models.Product).filter(models.Product.id == id).first()

    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Produsul cu id-ul {id} nu exista!')
    
    reviews = db.query(models.Review).filter(models.Review.product_id == id).all()

    return reviews

@router.post("")
def post_product(
    id: str = Form(...),
    name: str = Form(...),
    item_gender: schemas.GenderEnum = Form(...),
    type: schemas.ItemTypesEnum = Form(...),
    price: float = Form(...),
    categories: Optional[List[enums.ItemCategoriesEnum]] = Form(None),
    primary_image: UploadFile = File(...),
    secondary_images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    token: dict = Depends(oauth2.verify_admin_token)
):
    item_data = schemas.ProductBase(id=id, name=name, item_gender=item_gender, type=type, price=price, categories=categories)

    if db.query(models.Product).filter(models.Product.id == item_data.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu id-ul {item_data.id} deja exista')
    
    if db.query(models.Product).filter(models.Product.name == item_data.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu numele {item_data.name} deja exista')
    
    if item_data.type == enums.ItemTypesEnum.tricou or item_data.type == enums.ItemTypesEnum.haina and not item_data.size in enums.SizesEnum._value2member_map_:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Dimensiunea aleasa este invalida')

    # Handle file upload
    upload_dir = "uploads"  # Make sure this directory exists
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, primary_image.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(primary_image.file, buffer)

    # Create new product instance
    new_item = models.Product(**item_data.model_dump())
    new_item.primary_image = file_path  # Save the file path in the database

    # Add to database
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item

@router.delete("/{id}")
def delete_product(id: str, db: Session = Depends(get_db)):
    deleted_product = db.query(models.Product).filter(models.Product.id == id).first()

    if not deleted_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu id-ul {id} nu exista')
    
    db.delete(deleted_product)
    db.commit()
    
    return { "status": status.HTTP_204_NO_CONTENT, "detail": f'Produsul cu id-ul {id} a fost sters cu succes' }