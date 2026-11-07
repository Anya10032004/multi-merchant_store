# Model --> model.py(This is where we define teh tabble)
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime, Integer, ForeignKey
from datetime import datetime
from app import db


class Users(db.Model):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String(255), unique=True)
    email : Mapped[str] = mapped_column(String(255))
    password : Mapped[str] = mapped_column(String(255))
    role : Mapped[str] = mapped_column(String(225))

    def info_users(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "password" : self.password,
            "email" : self.email,
            "role" : self.role
        }


class Merchants(db.Model):
    __tablename__ = "merchants"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_name : Mapped[str] = mapped_column(String(255))
    description : Mapped[str] = mapped_column(String(255))
    id_user : Mapped[int] = mapped_column(ForeignKey("users.id"))
    adress : Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(255))

    def info_merchants(self):
        return {
            "id" : self.id,
            "store_name" : self.store_name,
            "description" : self.description,
            "id_user" : self.id_user,
            "adress" : self.adress,
            "phone": self.phone,
        }

class Products(db.Model):
    __tablename__ = "products"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name : Mapped[str] = mapped_column(String(255))
    description : Mapped[str] = mapped_column(String(255))
    price : Mapped[int] = mapped_column(Integer)
    stock : Mapped[int] = mapped_column(Integer)
    id_merchant : Mapped[int] = mapped_column(ForeignKey("merchants.id"))


    def info_products(self):
        return {
            "id" : self.id,
            "product_name" : self.product_name,
            "description" : self.description,
            "price" : self.price,
            "stock" : self.stock,
            "id_merchant" : self.id_merchant,
        }

class Claims(db.Model):
    __tablename__ = "claims"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_product : Mapped[int] = mapped_column(ForeignKey("products.id"))
    id_user : Mapped[int] = mapped_column(ForeignKey("users.id"))
    quantity : Mapped[int] = mapped_column(Integer)
    create_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def info_claims(self):
        return {
            "id" : self.id,
            "id_product" : self.id_product,
            "id_user" : self.id_user,
            "quantity" : self.quantity,
            "create_at" : self.create_at.isoformat()
        }