from sqlalchemy import func
from app.database import get_db
from app import models, oauth2, schemas
from fastapi import status, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

router = APIRouter(
    tags=['Reviews'],
    prefix="/reviews"
)

def update_rating(product_id: str, db: Session):
    avg_rating = db.query(func.avg(models.Review.stars))\
                  .filter(models.Review.product_id == product_id)\
                  .scalar()
    
    if avg_rating is not None:
        db.query(models.Product)\
          .filter(models.Product.id == product_id)\
          .update({"rating": round(avg_rating, 2)})
        db.commit()

@router.post("/{product_id}", response_model=schemas.ReviewResponse)
def post_review(product_id: str, message: str = Form(None), stars: int = Form(...), token: dict = Depends(oauth2.decode_authorization_token_with_exception), db: Session = Depends(get_db)):
    if not 1 <= stars <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Stars must be between 1 and 5"
        )

    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Produsul cu id-ul {product_id} nu exista')
    
    existing_review = db.query(models.Review)\
                        .filter(models.Review.product_id == product_id, models.Review.user_id == token.get("user_id"))\
                        .first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reviewed this product")
    
    review_data = schemas.ReviewBase(product_id=product_id, user_id=token.get("user_id"), message=message, stars=stars)

    new_review = models.Review(**review_data.model_dump())

    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
    
        update_rating(product_id, db)
        
        return new_review
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):

    review = db.query(models.Review).filter(models.Review.id == review_id).first()

    db.delete(review)
    db.commit()