from pydantic import BaseModel, Field
from typing import List

# 🔹 PRODUCT SCHEMAS

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    barcode: str
    price: float = Field(..., gt=0)
    gst: float = Field(..., ge=0)
    stock: float = Field(..., ge=0)   # ✅ changed to float


class ProductResponse(BaseModel):
    id: int
    name: str
    barcode: str
    price: float
    gst: float
    stock: float   # ✅ changed to float

    class Config:
        from_attributes = True


# 🔹 CART / BILLING SCHEMAS

class CartItem(BaseModel):
    product_id: int
    quantity: float   # ✅ IMPORTANT FIX


class BillCreate(BaseModel):
    items: List[CartItem]




class BillItemResponse(BaseModel):
    product_id: int
    quantity: float
    price: float
    gst: float
    total: float


class BillResponse(BaseModel):
    bill_id: int
    items: List[BillItemResponse]
    total: float