import json
from typing import  Optional
from app.database import get_db
from app import models, oauth2, schemas
from fastapi import Form, status, HTTPException, Depends, APIRouter, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone
from hashlib import sha256

router = APIRouter(
    tags=['Carts'],
    prefix="/carts"
)

def generate_cart_item_hash(user_id: str, product_id: str, personalised_fields: dict):
    to_hash = {
        "user_id": user_id, \
        "product_id": product_id, \
        "personalised_fields": dict(sorted(personalised_fields.items()))
    }

    json_str = json.dumps(to_hash, sort_keys=True)

    return sha256(json_str.encode('utf-8')).hexdigest()

def merge_carts(user_id: str, guest_id: str, db: Session):
    try:
        guest_cart_items = db.query(models.Cart).filter(models.Cart.guest_id == guest_id).all()
        if not guest_cart_items:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Cosul de cumparaturi al vizitatorului este gol")
        
        for guest_cart_item in guest_cart_items:
            guest_cart_item.user_id = user_id
            guest_cart_item.guest_id = None
        
        db.commit()  # Commit once after all updates
        return guest_cart_items
        
    except HTTPException:
        raise
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la unificarea cosurilor: {str(e)}"
        )

@router.post("", status_code=status.HTTP_201_CREATED)
def add_to_cart(
    product_id: str = Form(...),
    quantity: int = Form(...),
    personalised_fields: str = Form(...),
    jwt_content: dict | None = Depends(oauth2.decode_authorization_token),
    guest_token_content: dict | None = Depends(oauth2.decode_guest_token),
    db: Session = Depends(get_db),
):
    try:
        found_product = db.query(models.Product).filter(models.Product.id == product_id).first()

        if not found_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Produsul cu id-ul {product_id} nu exista')

        user_id = jwt_content.get("user_id") if jwt_content else None
        guest_id = guest_token_content.get("guest_user_id") if (not user_id and guest_token_content) else None

        if not user_id and not guest_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Niciun identificator nu a fost oferit in request")
        if user_id and guest_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ambele identificatoare au fost gasite in request")
        
        query_filter = models.Cart.user_id == user_id if user_id else models.Cart.guest_id == guest_id
        item_hash = generate_cart_item_hash(user_id, product_id, json.loads(personalised_fields))

        existing_cart_item = db.query(models.Cart).filter(query_filter, models.Cart.hash == item_hash).first()

        if existing_cart_item:
            existing_cart_item.quantity += quantity

            if (existing_cart_item.quantity < 1):
                db.delete(existing_cart_item)
                db.commit()
                return { "status": status.HTTP_204_NO_CONTENT, "detail": f'Obiectul a fost sters cu succes din cos' }
            
            existing_cart_item.created_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing_cart_item)

            return { "status": status.HTTP_200_OK, \
                     "detail": "Cantitatea din cos a obiectului a fost modificata cu succes", \
                     "item": existing_cart_item, \
                     "changed_quantity": "yes" }
        
        else:
            cart_item_data = schemas.CartItemBase(
                product_id=product_id, 
                quantity=quantity, 
                product_name=found_product.name,
                product_type=found_product.type,
                product_price=found_product.price,
                personalised_fields=personalised_fields,
                product_primary_image=found_product.primary_image,
            )

            cart_item = models.Cart(user_id=user_id, guest_id=guest_id, hash=item_hash, **cart_item_data.model_dump())
            
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)

            return { "status": status.HTTP_201_CREATED, "detail": "Obiectul a fost adaugat cu succes in cos", "item": cart_item }
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format in personalised_data"
        )
    
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"O eroare neasteptata s-a petrecut: {str(e)}"
        )

@router.get("", response_model=list[schemas.CartItemResponse])
def get_cart(jwt_content: dict | None = Depends(oauth2.decode_authorization_token), guest_token_content: dict | None = Depends(oauth2.decode_guest_token), db: Session = Depends(get_db)):
    user_id = jwt_content.get("user_id") if jwt_content else None
    guest_id = guest_token_content.get("guest_user_id") if (not user_id and guest_token_content) else None

    if not user_id and not guest_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Niciun identificator nu a fost oferit in headerele requestului")
    if user_id and guest_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ambele identificatoare au fost gasite in headerele requestului") 
    
    query_filter = models.Cart.user_id == user_id if user_id else models.Cart.guest_id == guest_id
    cart_items = db.query(models.Cart).filter(query_filter).all()

    return [schemas.CartItemResponse.model_validate({**item.__dict__, "personalised_fields": json.dumps(item.personalised_fields)}) for item in cart_items]

@router.delete("")
def delete_cart(cart_item_id: Optional[int] = None, \
                jwt_content: dict | None = Depends(oauth2.decode_authorization_token), \
                guest_token_content: dict | None = Depends(oauth2.decode_guest_token), \
                db: Session = Depends(get_db)):
    if not jwt_content and not guest_token_content:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tokenul de autentificare nu exista in headerele requestului")
    
    user_id = None
    guest_id = None
    
    if jwt_content:
        user_id = jwt_content.get("user_id")

    if guest_token_content:
        guest_id = guest_token_content.get("guest_user_id")
    
    if cart_item_id:
        existing_cart_item = db.query(models.Cart).filter(models.Cart.id == cart_item_id).first()

        if existing_cart_item and (existing_cart_item.user_id == user_id or existing_cart_item.guest_id == guest_id):
            db.delete(existing_cart_item)
            db.commit()
            return {"status": status.HTTP_200_OK, "detail": f'Obiectul cu id-ul {cart_item_id} a fost eliminat cu succes din cos'}
        
        return {"status": status.HTTP_404_NOT_FOUND, "detail": f'Obiectul cu id-ul {cart_item_id} nu exista in cosul tau de cumparaturi'}

    db.query(models.Cart).filter(or_(models.Cart.user_id == user_id, models.Cart.guest_id == guest_id)).delete()
    db.commit()

    return {"status": status.HTTP_200_OK, "detail": "Cosul a fost golit cu succes"}