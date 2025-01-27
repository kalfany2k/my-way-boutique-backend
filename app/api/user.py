from app.database import get_db
from app import models, schemas, utils, oauth2
from app.api.carts import merge_carts
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import ValidationError

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, guest_token_content: dict | None = Depends(oauth2.decode_guest_token), db: Session = Depends(get_db)):
    try:
        # Validate user data
        schemas.UserCreate(**user.model_dump())
        
        # Check for existing email
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email deja inregistrat")
        
        # Hash password and create user
        user.password = utils.hash(user.password)
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Try to merge carts if guest token exists
        if guest_token_content:
            try:
                merge_carts(new_user.id, guest_token_content.get("guest_user_id"), db)
            except HTTPException as e:
                if e.status_code != status.HTTP_204_NO_CONTENT:
                    # Only re-raise if it's not a "cart empty" message
                    raise
            
        return status.HTTP_201_CREATED
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"O eroare neasteptata s-a petrecut: {str(e)}"
        )

@router.get("/verify-admin")
def verify_admin(token: dict = Depends(oauth2.verify_admin_token), db: Session = Depends(get_db)):
    return { "status": "verified" }


@router.put("/admin/{id}", response_model=schemas.UserResponse)
def change_role(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizatorul nu exista")
    
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Utilizatorul este deja administrator")

    user.role = "admin"
    db.commit()
    
    return user

@router.get("/{id}", response_model=schemas.UserBase)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Utilizatorul cu id-ul {id} nu a fost gasit")
    
    return user