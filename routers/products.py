from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal
from routers.user import get_current_user
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 CREATE PRODUCT (ADMIN ONLY)
@router.post("/")
def add_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")



    db_product = models.Product(**product.dict())

    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

    except IntegrityError as e:
        db.rollback()

        if "barcode" in str(e.orig):
            msg = "Barcode already exists"
        elif "name" in str(e.orig):
            msg = "Product name already exists"
        else:
            msg = "Duplicate entry"

        raise HTTPException(status_code=400, detail=msg)

    return db_product


# 🔹 GET ALL PRODUCTS
@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@router.get("/{barcode}")
def get_product(barcode: str, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.barcode == barcode).first()

    if not product:
        return {"error": "NOT_FOUND"}   # faster than exception

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "gst": product.gst,
        "stock": product.stock
    }


# 🔹 UPDATE PRODUCT (ADMIN ONLY)
@router.put("/{id}")
def update_product(
    id: int,
    data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    product = db.query(models.Product).filter(models.Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in data.dict().items():
        setattr(product, key, value)

    db.commit()
    return product


# 🔹 DELETE PRODUCT (ADMIN ONLY)
@router.delete("/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    product = db.query(models.Product).filter(models.Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"msg": "Deleted successfully"}