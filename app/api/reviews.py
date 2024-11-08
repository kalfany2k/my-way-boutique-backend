from app.database import get_db
from app import models, oauth2, schemas
from fastapi import status, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

router = APIRouter(
    tags=['Reviews'],
    prefix="/reviews"
)

@router.post("/{product_id}", response_model=schemas.ReviewBase)
def post_review(product_id: str, message: str = Form(None), stars: int = Form(...), token: dict = Depends(oauth2.decode_token), db: Session = Depends(get_db)):
    if not db.query(models.Product).filter(models.Product.id == product_id).first():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Produsul cu id-ul {product_id} nu exista')
    
    review_data = schemas.ReviewBase(product_id=product_id, user_id=token.get("user_id"), message=message, stars=stars)

    new_review = models.Review(**review_data.model_dump())

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review