from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
from routers.user import get_current_user
from decimal import Decimal

router = APIRouter(prefix="/billing", tags=["Billing"])


# 🔹 DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create-bill")
def create_bill(
    data: schemas.BillCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    total = 0

    # 🔹 Create Bill
    bill = models.Bill(
    user_id=current_user.id,
    user_name=current_user.username,  # ✅ ADD THIS
    total=0
)

    db.add(bill)
    db.commit()
    db.refresh(bill)


    for item in data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 🔥 Convert quantity to Decimal
        quantity = Decimal(str(item.quantity))

        # 🔥 STOCK VALIDATION
        if product.stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        # 🔥 PRICE CALCULATION (SAFE)
        base_price = product.price * quantity

        gst_percent = Decimal(str(product.gst))
        gst_amount = base_price * (gst_percent / Decimal("100"))

        item_total = base_price + gst_amount

        total += item_total

        # 🔥 REDUCE STOCK
        product.stock -= quantity

        # 🔹 Save Bill Item
        bill_item = models.BillItem(
            bill_id=bill.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price,
            gst=product.gst
        )

        db.add(bill_item)

    # 🔹 Update total
    bill.total = total

    db.commit()

    return {
        
        "bill_id": bill.id,
        "total": float(total)
    }


# 🔹 GET ALL BILLS (ADMIN ONLY)
@router.get("/")
def get_all_bills(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    return db.query(models.Bill).all()


@router.get("/{bill_id}")
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    items = db.query(models.BillItem).filter(models.BillItem.bill_id == bill_id).all()
    
    result = []
    
    for item in items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    
        result.append({
            "name": product.name,
            "price": item.price,
            "gst": item.gst,
            "quantity": item.quantity
        })

    return {
        "bill_id": bill.id,
        "total": bill.total,
        "staff_name": bill.user_name,
        "items": result
    }