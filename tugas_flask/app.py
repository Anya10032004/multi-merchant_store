# mapped_collection
from flask import Flask, jsonify, request
import json
from datetime import datetime
import requests
from enum import unique
import os
from sqlalchemy import create_engine, String, DateTime, select, text, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Session, Mapped
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, get_jwt, jwt_required, get_jwt_identity, create_access_token
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
app_toko.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/db_store"

# Connect the app with the Flask-SQLAlchemy  by initialising the db object from the class SQLAlchemy
# This will be used for CRUD operation in the future and create tables in the database
db = SQLAlchemy(app_toko)
jwt = JWTManager(app_toko) # This is for generating JWT Token

app_toko.config["JWT_SECRET_KEY"] = "KunciRahasiaKitaBisaSajaGanti" # this is to set the secret key for the JWT token, 
                                                                      # it is a string that will be used to sign the JWT token
                                                                      # it is a random string, not a password, it is used to verify the token
                                                                      # this will expire in 24 hours, change as you wish

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

@app_toko.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    namee = data.get("name")
    emaill = data.get("email")
    passwordd = data.get("password")
    rolee = data.get("role").lower()
    hash_password = generate_password_hash(passwordd)
    role_list = ["user", "merchant"]
    if not namee or not emaill or not passwordd or not rolee:
        return jsonify(
            {
                "message": "Missing required fields", 
                "status": 400
            }
        ), 400
    
    if rolee not in role_list:
        return jsonify(
            {
                "message": "Invalid role", 
                "status": 401
            }
        ), 401
    print(hash_password)

    
    # Acess the database
    with Session(bind=db.engine) as session:
        new_users = Users(name=namee, email=emaill, password=hash_password, role=rolee)
        session.add(new_users)
        session.commit()
        return jsonify({"message": "User added successfully", "status": 201, "data": new_users.info_users()}), 201
    

@app_toko.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    emaill = data.get("email")
    passwordd = data.get("password")

    if not emaill or not passwordd:
        return jsonify({"message": "Missing required fields", "status": 400}), 400
    
    
    # Acess the database
    with Session(bind=db.engine) as session: # this code is to acesss session, session is for interacting with the database, 
                                             # it will create a temporary session to interact with the database and close it after the interaction
        users = session.scalars(select(Users).where(Users.email == emaill)).first() # this code is to select a user from the database based on the email 
                                                                                                                       # and password provided, 
                                                                                                                       # where() is to filter the data, and 
                                                                                                                       # .first() is to get the first result
        if users and check_password_hash(users.password, passwordd):
            # Login sicessfuly, we will make the token
            token = create_access_token(
                identity = str(users.id),
                additional_claims={
                    "id": users.id,
                    "name": users.name,
                    "email": users.email,
                    "password": users.password,
                    "role": users.role
                }
            )

            return jsonify(
                {"message": "Login successful", 
                "status": 200, 
                "data": users.info_users(),
                "Acess Token": token}
                ), 200


        return jsonify({"message": "Invalid email or password", "status": 401}), 401

@app_toko.route("/api/merchants", methods=["POST"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def merchants():
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    data = request.get_json()
    store_namee = data.get("store_name")
    description = data.get("description")
    id_user = data.get("id_user")
    adress = data.get("adress")
    phone = data.get("phone")

    if not store_namee:
        return jsonify(
            {
                "message": "Store name is required", 
                "status": 400
            }
        ), 400
    
    # Acess the database
    with Session(bind=db.engine) as session:
        checkk = session.scalars(select(Merchants).where(Merchants.store_name == store_namee)).all()
        if len(checkk) > 0:
            return jsonify({"message": "That store name is already taken", "status": 400}), 400
        new_merchants = Merchants(store_name=store_namee, description=description, id_user=id_user, adress=adress, phone=phone)
        session.add(new_merchants)
        session.commit()
        return jsonify({"message": "Merchants added successfully", "status": 201, "data": new_merchants.info_merchants()}), 201

@app_toko.route("/api/merchant/me", methods=["GET"])
def get_my_merchant():
    # Acess the database
    with Session(bind=db.engine) as session:
        merchant = session.scalars(select(Merchants).where(Merchants.id_user == session["id"])).first()
        if merchant:
            return jsonify({"message": "Merchant found", "status": 200, "data": merchant.info_merchants()}), 200
        return jsonify({"message": "Merchant not found", "status": 404}), 404
    
@app_toko.route("/api/merchant/me", methods  = ["PUT"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def update_my_merchant():
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    data = request.get_json()
    store_name = data.get("store_name")
    description = data.get("description")
    adress = data.get("adress")
    phone = data.get("phone")
    # Acess the database
    with Session(bind=db.engine) as session:
        merchant = session.scalars(select(Merchants).where(Merchants.id_user == session["id"])).first()
        if merchant:
            if "store_name" in data:
                merchant.store_name = store_name
            if "description" in data:
                merchant.description = description
            if "adress" in data:
                merchant.adress = adress
            if "phone" in data:
                merchant.phone = phone
            session.commit()
            return jsonify({"message": "Merchant updated successfully", "status": 200, "data": merchant.info_merchants()}), 200
        return jsonify({"message": "Merchant not found", "status": 404}), 404


@app_toko.route("/api/merchants", methods  = ["GET"])
def get_merchants():
    # Acess the database
    with Session(bind=db.engine) as session:
        merchants = session.scalars(select(Merchants).order_by(Merchants.id.desc())).all()
        if merchants:
            return jsonify({"message": "Merchant found", "status": 200, "data": [m.info_merchants() for m in merchants]}), 200
        return jsonify({"message": "Merchant not found", "status": 404}), 404
          
@app_toko.route("/api/merchants/<int:id>", methods  = ["GET"])
def get_merchants_id(id):
    with Session(bind=db.engine) as session:
        merchant = session.scalars(select(Merchants.store_name, Products.name, Products.price, Products.stock).join(Products, Merchants.id == Products.merchant_id).filter(Merchants.id == id)).all()
        if merchant:
            return jsonify({"message": "Merchant found", "status": 200, "data": merchant}), 200
        return jsonify({"message": "Merchant not found", "status": 404}), 404          


# PRODUCT
@app_toko.route("/api/products", methods = ["POST"])
@ jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def product():
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    
    with Session(bind=db.engine) as session:
        merchant_id = session.scalars(select(Merchants.id).where(Merchants.id_user == session["id"])).first()
        if not merchant_id:
            return jsonify({"message": "No profile for Merchant is found, please create one first", "status": 400}), 400

    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock")

    if price < 0 or stock < 0:
        return jsonify({"message": "Price and stock cannot be negative", "status": 400}), 400
    

    if not name or not description or not price or not stock:
        return jsonify({"message": "Missing required fields", "status": 400}), 400

    
    with Session(bind=db.engine) as session:
        merchant_id = session.scalars(select(Merchants.id).where(Merchants.id_user == session["id"])).first()
        if not merchant_id:
            return jsonify({"message": "You are not a merchant", "status": 403}), 403
        new_product = Products(name=name, description=description, price=price, stock=stock, merchant_id = merchant_id)
        session.add(new_product)
        session.commit()
        return jsonify({"message": "Product added successfully", "status": 201, "data": new_product.info_product()}), 201

@app_toko.route("/api/products/mine", methods = ["GET"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def get_products():
     # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    with Session(bind=db.engine) as session:
        new_product = session.scalars(select(Products).where(Products.id == session["id"])).first()
        if new_product:
            return jsonify({"message": "List of yoru products", "status": 200, "data": [p.info_product() for p in new_product]}), 200
        return jsonify({"message": "You don't have any products", "status": 404}), 404

@app_toko.route("/api/products/<int:product_id>", methods = ["PUT"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def update_products(product_id):
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    data = request.get_json()
    name = data.get("name")
    Merchant_id = data.get("merchant_id")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock")

    if price < 0 or stock < 0:
        return jsonify({"message": "Price and stock cannot be negative", "status": 400}), 400

    if Merchant_id != session["id"]:
        return jsonify({"message": "You are not the owner of this merchant", "status": 403}), 403

    with Session(bind=db.engine) as session:
        product = session.scalars(select(Products).where(Products.id == product_id and Products.id_merchant == Merchant_id)).first()
        if product:
            if "name" in data:
                product.name = name
            if "description" in data:
                product.description = description
            if "price" in data:
                product.price = price
            if "stock" in data:
                product.stock = stock
            session.commit()
            return jsonify({"message": "Product updated successfully", "status": 200, "data": product.info_product()}), 200
        return jsonify({"message": "Product not found", "status": 404}), 404

@app_toko.route("/api/products/<int:product_id>", methods = ["DELETE"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def delete_products(product_id):
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })

    with Session(bind=db.engine) as session:
        product = session.scalars(select(Products).where(Products.id == product_id and Products.id_merchant == session["merchant_id"])).first()
        if not product:
            return jsonify({"message": f"No product with the given ID {product_id} or not owned by merchant with ID {session['merchant_id']}", "status": 403}), 403
        session.delete(product)
        session.commit()
        return jsonify({"message": "Product deleted successfully", "status": 200}), 200

# CATALOG
@app_toko.route("/api/catalog", methods = ["GET"])    
def catalog():
    with Session(bind=db.engine) as session:
        products = session.scalars(select(Products).order_by(Products.id.desc())).all()
        if products:
            return jsonify({"message": "List of products", "status": 200, "data": [p.info_product() for p in products if p.stock > 0]}), 200
        return jsonify({"message": "No products found", "status": 404}), 404

@app_toko.route("/api/catalog/<int:product_id>", methods = ["GET"])
def get_catalog(product_id):
    with Session(bind=db.engine) as session:
        product = session.scalars(select(Products).where(Products.id == id)).first()
        if product:
            return jsonify({"message": "Product found", "status": 200, "data": product.info_product()}), 200
        return jsonify({"message": "Product not found", "status": 404}), 404

@app_toko.route("/api/claims", methods = ["POST"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def claim_product():
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "user":
        return jsonify({
            "error": "You have no access because you are not a User"
        })

    data = request.get_json()
    product_id = data.get("product_id")
    amount = data.get("amount")
    if not product_id or not amount:
        return jsonify({"message": "Missing required fields", "status": 400}), 400
    
    with Session(bind=db.engine) as session:
        prod = session.scalars(select(Products).where(Products.id == product_id)).first()
        if not prod:
            return jsonify({"message": "Product not found", "status": 404}), 404
        if amount > prod.stock:
            return jsonify({"message": f"Not enough stock, only {prod.stock} left", "status": 400}), 400
        prod.stock -= amount
        session.add(prod)
        session.commit()
        new_claim = Claims(id_product=product_id, amount=amount, id_user=token_acess.get("id"))
        session.add(new_claim)
        session.commit()
        return jsonify({"message": "Claim added successfully", "status": 201, "data": new_claim.info_claim()}), 201

@app_toko.route("/api/claims", methods = ["GET"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def get_claims():
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "user":
        return jsonify({
            "error": "You have no access because you are not a User"
        })
    if "id" not in session:
        return jsonify({"message": "You are not logged in", "status": 401}), 401
    if session["role"] != "USER":
        return jsonify({"message": "You are not a user", "status": 403}), 403
    with Session(bind=db.engine) as session:
        claims = session.scalars(select(Claims).order_by(Claims.id.desc())).all()
        if claims:
            return jsonify({"message": "List of claims", "status": 200, "data": [c.info_claim() for c in claims]}), 200
        return jsonify({"message": "No claims found", "status": 404}), 404



    
if __name__ == "__main__":
    app_toko.run(debug=True)