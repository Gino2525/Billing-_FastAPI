from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base
from sqlalchemy import Numeric
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    barcode = Column(String, unique=True, index=True)
    price = Column(Numeric(10, 2))
    gst = Column(Numeric(5, 2))   
    stock = Column(Numeric(10, 3))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String)   
    total = Column(Numeric(10, 2))


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Numeric(10, 3))
    price = Column(Numeric(10, 2))
    gst = Column(Numeric(5, 2))

