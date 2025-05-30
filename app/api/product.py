from typing import Optional
from sqlalchemy import func
from app import models, oauth2, schemas, enums
from app.database import get_db
from app.s3 import upload_file_to_s3, delete_file_from_s3
from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, contains_eager
from typing import List

router = APIRouter(
    tags=['Products'],
    prefix="/products"
)

@router.get("", response_model=schemas.QueryResponse)
def get_products(categories: Optional[str] = Query(None), search: Optional[str] = Query(None), 
                 sort_by: Optional[str] = Query(None), type: Optional[str] = Query(None), 
                 set_type: Optional[str] = Query(None), gender: Optional[str] = Query(None), 
                 skip: int = Query(default=0, ge=0),  limit: int = 16, db: Session = Depends(get_db)
                ):
    query = db.query(models.Product)

    # Apply search term
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))

    # Apply categories
    if categories:
        categories = categories.split("+")
        query = query.filter(models.Product.categories.contains(categories))

    # Apply type
    if type:
        try:
            type = enums.ItemTypesEnum[type]
            query = query.filter(models.Product.type == type)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Tipul de produs {type} nu exista')
        
    if type == "set" and set_type:
        # If we are querying sets, then we can inner join and retrieve only those.
        query = query.join(models.ProductSet).filter(models.ProductSet.set_type == set_type)
    else:
        # Otherwise, use outer join to retrieve all results.
        query = query.outerjoin(models.ProductSet)

    # Apply gender 
    if gender:
        gender_map = {"fete": "F", "baieti": "M"}
        gender_value = gender_map.get(gender, "U")
        query = query.filter(models.Product.item_gender == gender_value)

    # Adds another field to the SELECT SQL statement, which counts the number of products the query has retrieved
    count_query = query.with_entities(func.count())
    # Transforms to number or None, given the count
    count = count_query.scalar()

    if sort_by:
        if sort_by == "recente":
            query = query.order_by(models.Product.created_at.desc())
        elif sort_by == "popularitate":
            query = query.order_by(models.Product.total_sales.desc())
        elif sort_by == "pret_asc":
            query = query.order_by(models.Product.price.asc())
        elif sort_by == "pret_desc":
            query = query.order_by(models.Product.price.desc())
    else:
        query = query.order_by(models.Product.created_at.desc())

    query = query.options(contains_eager(models.Product.product_set))

    products = query.offset(skip * limit).limit(min(limit, 16)).all()

    return {"items": products, "count": count}

@router.get("/{id}")
def get_product(id: str, db: Session = Depends(get_db)):
    found_post = db.query(models.Product).filter(models.Product.id == id).first()

    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Produsul cu id-ul {id} nu exista!')
    
    return found_post

@router.get("/{product_id}/reviews", response_model=List[schemas.ReviewResponse])
def get_product_reviews(product_id: str, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.product_id == product_id).all()

    return reviews

@router.post("")
async def post_product(
    id: str = Form(...),
    name: str = Form(...),
    item_gender: schemas.GenderEnum = Form(...),
    type: schemas.ItemTypesEnum = Form(...),
    price: float = Form(...),
    categories: Optional[List[enums.ItemCategoriesEnum]] = Form(None),
    primary_image: UploadFile = File(...),
    secondary_images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    token: dict = Depends(oauth2.verify_admin_token)
):
    item_data = schemas.ProductBase(id=id, name=name, item_gender=item_gender, type=type, price=price, categories=categories)
    MAX_SIZE = 5 * 1024 * 1024  # 5MB

    if id.find(" ") != -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Id-ul produsului nu poate contine spatii')

    if db.query(models.Product).filter(models.Product.id == item_data.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu id-ul {item_data.id} deja exista')
    
    if db.query(models.Product).filter(models.Product.name == item_data.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu numele {item_data.name} deja exista')
    
    if item_data.type == enums.ItemTypesEnum.tricou or item_data.type == enums.ItemTypesEnum.haina and not item_data.size in enums.SizesEnum._value2member_map_:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Dimensiunea aleasa este invalida')
    
    if int(primary_image.headers.get('content-length', 0)) > MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f'Dimensiunea imaginii principale este mai mare de 5MB')
    
    if secondary_images:
        for image in secondary_images:
            if int(image.headers.get('content-length', 0)) > MAX_SIZE:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f'Dimensiunea imaginii {image.filename} este mai mare de 5MB')

    try:
        primary_image_url = await upload_file_to_s3(primary_image, item_data.type.value)
        secondary_images_urls = []
        if secondary_images:
            for image in secondary_images:
                url = await upload_file_to_s3(image, item_data.type.value)
                secondary_images_urls.append(url)

        # Create new product instance
        new_item = models.Product(**item_data.model_dump())
        new_item.primary_image = primary_image_url
        new_item.secondary_images = secondary_images_urls

        # Add to database
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return { "status": status.HTTP_201_CREATED }
    except Exception as e:
        db.rollback()
        raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail=str(e)
       )

@router.delete("/{id}")
async def delete_product(id: str, db: Session = Depends(get_db)):
    deleted_product = db.query(models.Product).filter(models.Product.id == id).first()

    if not deleted_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Produsul cu id-ul {id} nu exista')
    
    try:
        if deleted_product.primary_image:
            key = deleted_product.primary_image.split('/')  # Get filename from URL
            if len(key) > 2:
                await delete_file_from_s3(key[-1], key[-2], db)

        if deleted_product.secondary_images:
            for image in deleted_product.secondary_images:
                key = image.split('/')
                if len(key) > 2:
                    await delete_file_from_s3(key[-1], key[-2], db)

        db.delete(deleted_product)
        db.commit()
       
        return {
           "status": status.HTTP_204_NO_CONTENT, 
           "detail": f'Produsul cu id-ul {id} a fost sters cu succes'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail=str(e)
       )