from app.database import get_db
from app import models, oauth2, schemas
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

router = APIRouter(
    tags=['Carts'],
    prefix="/carts"
)

@router.post("/{item_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.CartItemBase)
def add_to_cart(item_id: str, quantity: int = 1, jwt_content: dict = Depends(oauth2.decode_token), db: Session = Depends(get_db)):
    if not db.query(models.Product).filter(models.Product.id == item_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu id-ul {item_id} nu exista')

    existing_cart_item = db.query(models.Cart).filter(models.Cart.user_id == jwt_content.get("user_id"), models.Cart.product_id == item_id).first()
    if existing_cart_item:
        existing_cart_item.quantity += quantity
        if existing_cart_item.quantity < 1:
            db.delete(existing_cart_item)
            db.commit()
            return { "status": status.HTTP_204_NO_CONTENT, "detail": "Obiectul a fost sters cu succes din cos" }
        existing_cart_item.created_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing_cart_item)

        return { "status": status.HTTP_200_OK, "detail": "Cantitatea din cos a obiectului a fost modificata cu succes" }

    cart_item = models.Cart(user_id=jwt_content.get("user_id"), quantity=quantity, product_id=item_id)

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return { "status": status.HTTP_201_CREATED, "detail": "Obiectul a fost adaugat cu succes in cos" }

@router.get("", response_model=list[schemas.CartItemBase])
def get_cart(jwt_content: dict = Depends(oauth2.decode_token), db: Session = Depends(get_db)):
    user_id = jwt_content.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentiale de autentificare invalide")

    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user_id).all()

    return [schemas.CartItemBase.model_validate(item) for item in cart_items]

@router.delete("")
def delete_cart(jwt_content: dict = Depends(oauth2.decode_token), db: Session = Depends(get_db)):
    user_id = jwt_content.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentiale de autentificare invalide")

    db.query(models.Cart).filter(models.Cart.user_id == user_id).delete()
    db.commit()

    return {"status": status.HTTP_200_OK, "detail": "Cosul a fost golit cu succes"}