from typing import Optional

from sqlalchemy import func
from app.database import get_db
from app import models, oauth2, schemas, enums
from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from typing import List

router = APIRouter(
    tags=['Sets'],
    prefix="/sets"
)

@router.post("")
def post_set(set_name: str = Form(...), product_ids: List[str] = Form(...), db: Session = Depends(get_db), token: dict = Depends(oauth2.verify_admin_token)):
    existing_set = db.query(models.Set).filter(models.Set.set_name == set_name).first()

    if existing_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Setul cu numele {set_name} deja exista')
    
    existing_products = db.query(models.Product.id).filter(models.Product.id.in_(product_ids)).all()
    existing_products_ids = {product[0] for product in existing_products}

    missing_products = set(product_ids) - existing_products_ids
    if missing_products:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsele cu id-urile {", ".join(missing_products)} nu exista')

    try:
        new_set = models.Set(set_name=set_name)
        db.add(new_set)
        db.flush()

        set_items = [models.SetItem(set_id=new_set.id, product_id=product_id) for product_id in product_ids]
        db.bulk_save_objects(set_items)

        db.commit()
        db.refresh(new_set)

        return new_set
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Nu s-a putut crea setul: {str(e)}")