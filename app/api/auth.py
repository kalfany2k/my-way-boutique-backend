from app.database import get_db
from app import models, oauth2, schemas, utils
from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from ..ses import send_email_via_ses

router = APIRouter(
    tags=['Login']
)

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credentiale invalide")
    
    if not utils.verify_hash(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credentiale invalide")

    access_token = oauth2.create_access_token(data={"user_id": user.id, "role": user.role})
    user_data = schemas.UserResponse.model_validate(user)

    return {"access_token": access_token, "token_type": "bearer", "user": jsonable_encoder(user_data)}

@router.get("/login_guest")
def create_guest_session():
    guest_token = oauth2.create_guest_token()

    return {"guest_token": guest_token}