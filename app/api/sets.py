from typing import Optional

from sqlalchemy import func
from app.api.product import post_product
from app.database import get_db
from app import models, oauth2, schemas, enums
from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from typing import List

from app.s3 import upload_file_to_s3

router = APIRouter(
    tags=['Sets'],
    prefix="/sets"
)

@router.post("")
async def post_set(
    id: str = Form(...),
    name: str = Form(...),
    item_gender: schemas.GenderEnum = Form(...),
    price: float = Form(...),
    categories: Optional[List[enums.ItemCategoriesEnum]] = Form(None),
    primary_image: UploadFile = File(...),
    secondary_images: Optional[List[UploadFile]] = File(None),
    set_type: str = Form(...),
    primary_product_ids: List[str] = Form(...),
    secondary_product_ids: Optional[List[str]] = Form(None), 
    db: Session = Depends(get_db), 
    token: dict = Depends(oauth2.verify_admin_token)
    ):

    if id.find(" ") != -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Id-ul setului nu poate contine spatii')
    
    existing_set = db.query(models.Product).filter(models.Product.id == id).first()

    if existing_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Setul cu id-ul {id} deja exista')

    for product_id in primary_product_ids:
        existing_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not existing_product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul principal cu id-ul {product_id} nu poate fi adaugat in set, nu exista')
        
    if secondary_product_ids:
        for product_id in secondary_product_ids:
            existing_product = db.query(models.Product).filter(models.Product.id == product_id).first()
            if not existing_product:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul secundar cu id-ul {product_id} nu poate fi adaugat in set, nu exista')

    try:
        # Create a new product of type set that will be displayed on the shopping page
        await post_product(id=id, name=name, item_gender=item_gender, type="set", price=price, categories=categories, primary_image=primary_image, secondary_images=secondary_images, db=db, token=token)

        # Create the entry linking the "additional details" to the product itself in a separate table
        set_data = schemas.SetBase(id=id, set_type=set_type, primary_product_ids=primary_product_ids, secondary_product_ids=secondary_product_ids)
        new_set = models.ProductSet(**set_data.model_dump())
        
        db.add(new_set)
        db.commit()
        db.refresh(new_set)

        return { "status": status.HTTP_201_CREATED }
    except Exception as e:
        db.rollback()
        raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail=str(e)
       )