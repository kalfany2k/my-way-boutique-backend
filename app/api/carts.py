from typing import Optional
from app.database import get_db
from app import models, oauth2, schemas
from fastapi import Form, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

router = APIRouter(
    tags=['Carts'],
    prefix="/carts"
)

@router.post("", status_code=status.HTTP_201_CREATED)
def add_to_cart(
    product_id: str = Form(...),
    quantity: int = Form(...),
    personalised_name: Optional[str] = Form(None),
    personalised_date: Optional[str] = Form(None), 
    personalised_message: Optional[str] = Form(None),
    personalised_size: Optional[str] = Form(None), 
    personalised_member: Optional[str] = Form(None), 
    jwt_content: dict = Depends(oauth2.decode_token), 
    db: Session = Depends(get_db)
):
    try:
        found_product = db.query(models.Product).filter(models.Product.id == product_id).first()

        if not found_product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu id-ul {cart_item_data.product_id} nu exista')

        cart_item_data = schemas.CartItemBase(
            product_id=product_id, 
            quantity=quantity, 
            product_name=found_product.name,
            product_type=found_product.type,
            product_price=found_product.price,
            product_primary_image=found_product.primary_image,
            personalised_name=personalised_name, 
            personalised_message=personalised_message,
            personalised_date=personalised_date,
            personalised_size=personalised_size,
            personalised_member=personalised_member
        )

        existing_cart_items = db.query(models.Cart).filter(models.Cart.user_id == jwt_content.get("user_id"), models.Cart.product_id == cart_item_data.product_id).all()
        if existing_cart_items:
            for cart_item in existing_cart_items:
                # compare all attributes to check if we are referring to the same object or not
                if all(
                    getattr(cart_item, field) == getattr(cart_item_data, field)
                    for field in ['personalised_name', 'personalised_date', 'personalised_member', 'personalised_message', 'personalised_size']
                    ):
                    # remove the intended quantity from the entry
                    cart_item.quantity += quantity

                    # if it is below 0, delete the cart item from the database
                    if (cart_item.quantity < 1):
                        db.delete(cart_item)
                        db.commit()
                        return { "status": status.HTTP_204_NO_CONTENT, "detail": f'Obiectul a fost sters cu succes din cos' }
                    
                    # refresh creation time
                    cart_item.created_at = datetime.now(timezone.utc)
                    db.commit()
                    db.refresh(cart_item)

                    return { "status": status.HTTP_200_OK, "detail": "Cantitatea din cos a obiectului a fost modificata cu succes", "item": cart_item, "changed_quantity": "yes" }

        if (quantity < 1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Cantitatea trebuie sa fie mai mare sau egala cu 1')

        cart_item = models.Cart(user_id=jwt_content.get("user_id"), **cart_item_data.model_dump())
        
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

        return { "status": status.HTTP_201_CREATED, "detail": "Obiectul a fost adaugat cu succes in cos", "item": cart_item }
    
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("", response_model=list[schemas.CartItemResponse])
def get_cart(jwt_content: dict = Depends(oauth2.decode_token), db: Session = Depends(get_db)):
    user_id = jwt_content.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentiale de autentificare invalide")

    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user_id).all()

    return [schemas.CartItemResponse.model_validate(item) for item in cart_items]

@router.delete("")
def delete_cart(cart_item_id: Optional[int] = None, jwt_content: dict = Depends(oauth2.decode_token), db: Session = Depends(get_db)):
    user_id = jwt_content.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentiale de autentificare invalide")
    
    if cart_item_id:
        existing_cart_item = db.query(models.Cart).filter(models.Cart.id == cart_item_id).first()
        if existing_cart_item:
            db.delete(existing_cart_item)
            db.commit()

            return {"status": status.HTTP_200_OK, "detail": f'Obiectul cu id-ul {cart_item_id} a fost eliminat cu succes din cos'}
        
        return {"status": status.HTTP_204_NO_CONTENT, "detail": f'Obiectul cu id-ul {cart_item_id} nu exista in cosul tau de cumparaturi'}

    db.query(models.Cart).filter(models.Cart.user_id == user_id).delete()
    db.commit()

    return {"status": status.HTTP_200_OK, "detail": "Cosul a fost golit cu succes"}