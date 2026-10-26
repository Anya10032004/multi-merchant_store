from flask import Flask, jsonify, request
import json
from datetime import datetime
import requests
from enum import unique
import os
from sqlalchemy import create_engine, String, DateTime, select, text, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Session, Mapped
from flask_sqlalchemy import SQLAlchemy

# Tabble --> users(register dan login), merchants, products. claims

# Connect The database
# user: root
# password: no password
# host: localhost(our computer,, kalau berjalan di server, ganti localhost menjadi IP server)
# port: 3306(ini adalah port default, bisa juga diubah sesuai dengan port mysql di komputer anda)
# database:  store_db

#format of the link to conect python to mysql: mysql+pymysql://user:password@host:port/nama_database
app_toko = Flask(__name__)

# Connecting The Database
app_toko.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/store_db"

# Connect the app with the Flask-SQLAlchemy  by initialising the db object from the class SQLAlchemy
# This will be used for CRUD operation in the future and create tables in the database
db = SQLAlchemy(app_toko)

# Model for Users Table
# The model below is used to represent the users table in the database. 
# It is a class that inherits from db.Model which mean it will become the table in the database.
# Every attribute in this class is the column in the database table.
class Users(db.Model):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String(255), unique=True)
    email : Mapped[str] = mapped_column(String(255))
    password : Mapped[str] = mapped_column(String(255))

    def info_users(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "password" : self.password,
            "email" : self.email,
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

# Create the tables
with app_toko.app_context():
    db.create_all()



# Check
@app_toko.route("/api", methods=["GET"])
def main():
    return jsonify({
        "message": "Welcome to the API",
        "status": 200,
        "data": None
    })

# ----------------------------------------------------------------- #
# Merchant

@app_toko.route("/api/users", methods=["POST"])
def add_users():
    data = request.get_json()
    namee = data.get("name")
    emaill = data.get("email")
    passwordd = data.get("password")

    if not namee or not emaill or not passwordd:
        return jsonify({"message": "Missing required fields", "status": 400}), 400
    
    # Acess the database
    with Session(bind=db.engine) as session:
        new_users = Users(name=namee, email=emaill, password=passwordd)
        session.add(new_users)
        session.commit()
        return jsonify({"message": "User added successfully", "status": 201, "data": new_users.info_users()}), 201
    

@app_toko.route("/api/users", methods=["GET"])
def get_all_users():
    with Session(bind=db.engine) as session:
        all_users = session.scalars(select(Users).order_by(Users.id.asc())).all()
        list_users = [users.info_users() for users in all_users]
        if list_users:
            return jsonify(
                {
                    "message": "Users retrieved successfully", 
                    "status": 200, 
                    "data": list_users
                }
            ), 200
        return jsonify({"message": "No users found", "status": 200, "data": None}), 200





    
if __name__ == "__main__":
    app_toko.run(debug=True)