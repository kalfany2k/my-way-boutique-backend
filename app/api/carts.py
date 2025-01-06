from typing import  Optional
from app.database import get_db
from app import models, oauth2, schemas
from fastapi import Form, status, HTTPException, Depends, APIRouter, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone

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
    jwt_content: dict | None = Depends(oauth2.decode_authorization_token),
    guest_token_content: dict | None = Depends(oauth2.decode_guest_token),
    db: Session = Depends(get_db),
):
    try:
        found_product = db.query(models.Product).filter(models.Product.id == product_id).first()

        if not found_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Produsul cu id-ul {cart_item_data.product_id} nu exista')

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

        user_id = None
        guest_id = None

        if jwt_content:
            user_id = jwt_content.get("user_id")
        if not user_id and guest_token_content:
            guest_id = guest_token_content.get("guest_user_id")

        if not user_id and not guest_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Niciun identificator nu a fost oferit in request")
        if user_id and guest_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ambele identificatoare au fost gasite in request")

        if user_id:
            query_filter = models.Cart.user_id == user_id
        elif guest_id:
            query_filter = models.Cart.guest_id == guest_id

        existing_cart_items = db.query(models.Cart).filter(query_filter, models.Cart.product_id == cart_item_data.product_id).all()
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

        cart_item = models.Cart(user_id=user_id, guest_id=guest_id, **cart_item_data.model_dump())
        
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
            detail=f"O eroare neasteptata s-a petrecut: {str(e)}"
        )
    
@router.post("/merge")
def merge_carts(jwt_content: dict | None = Depends(oauth2.decode_authorization_token), guest_token_content: dict | None = Depends(oauth2.decode_guest_token), db: Session = Depends(get_db)):
    if not jwt_content or not guest_token_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id sau guest_id invalid"
        )
    
    user_id = jwt_content.get("user_id")
    guest_id = guest_token_content.get("guest_user_id")
    
    try:
        user_cart_item = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
        if user_cart_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Utilizatorul cu id-ul {user_id} are deja produse in cos'
            )

        guest_cart_items = db.query(models.Cart).filter(models.Cart.guest_id == guest_id).all()

        if not guest_cart_items:
            return {
                "status_code": status.HTTP_200_OK,
                "detail": "Nu exista produse in cosul guestului pentru transfer"
            }
        
        for guest_cart_item in guest_cart_items:
            guest_cart_item.guest_id = None
            guest_cart_item.user_id = user_id

        db.commit()

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Cosurile au fost unite cu succes"
        }

    except HTTPException as he:
        db.rollback()
        raise he

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"O eroare neasteptata s-a petrecut: {str(e)}"
        )

@router.get("", response_model=list[schemas.CartItemResponse])
def get_cart(jwt_content: dict | None = Depends(oauth2.decode_authorization_token), guest_token_content: dict | None = Depends(oauth2.decode_guest_token), db: Session = Depends(get_db)):
    if not jwt_content or not guest_token_content:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="")
    
    user_id = jwt_content.get("user_id")

    if not user_id:
        guest_id = guest_token_content.get("guest_user_id")

    if user_id:
        query_filter = models.Cart.user_id == user_id
    elif guest_id:
        query_filter = models.Cart.guest_id == guest_id

    cart_items = db.query(models.Cart).filter(query_filter).all()

    return [schemas.CartItemResponse.model_validate(item) for item in cart_items]

@router.delete("")
def delete_cart(cart_item_id: Optional[int] = None, jwt_token: str | None = Cookie(None, alias="authToken"), guest_token: str | None = Cookie(None, alias="guestSessionToken"), db: Session = Depends(get_db)):
    user_id = None
    guest_id = None

    if jwt_token:
        user_id = oauth2.decode_authorization_token_with_exception(jwt_token).get("user_id")
    if not jwt_token and guest_token:
        guest_id = oauth2.decode_guest_token_with_exception(guest_token).get("guest_user_id")

    if not user_id:
        user_id = guest_id
    
    if cart_item_id:
        existing_cart_item = db.query(models.Cart).filter(models.Cart.id == cart_item_id).first()
        if existing_cart_item and (existing_cart_item.user_id == user_id or existing_cart_item.guest_id == guest_id):
            db.delete(existing_cart_item)
            db.commit()
            return {"status": status.HTTP_200_OK, "detail": f'Obiectul cu id-ul {cart_item_id} a fost eliminat cu succes din cos'}
        
        return {"status": status.HTTP_204_NO_CONTENT, "detail": f'Obiectul cu id-ul {cart_item_id} nu exista in cosul tau de cumparaturi'}

    db.query(models.Cart).filter(models.Cart.user_id == user_id).delete()
    db.commit()

    return {"status": status.HTTP_200_OK, "detail": "Cosul a fost golit cu succes"}