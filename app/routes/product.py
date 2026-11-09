from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import  Session
from flask_jwt_extended import  get_jwt, jwt_required, get_jwt_identity
from app import db
from app.models import Merchants, Products

products_bp = Blueprint("products", __name__)

@products_bp.route("/products", methods = ["POST"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def product():
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    id = get_jwt_identity()
    with Session(bind=db.engine) as session:
        merchant_id = session.scalars(select(Merchants.id).where(Merchants.id_user == id)).first()
        if not merchant_id:
            return jsonify({"message": "No profile for Merchant is found, please create one first", "status": 400}), 400

    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock")
    

    if not name or not description or not price or not stock:
        return jsonify({"message": "Missing required fields", "status": 400}), 400
    
    if price is not None or stock is not None:
        if price.isdigit() == False or stock.isdigit() == False:
            return jsonify({
                "message": "Contains digit only",
                "status": 400
            }), 400
        if int(price) < 0 or int(stock) < 0 :
            return jsonify({"message": "Price and stock cannot be negative", 
            "status": 400}), 400
    
    with Session(bind=db.engine) as session:
        merchant_id = session.scalars(select(Merchants.id).where(Merchants.id_user == id)).first()
        if not merchant_id:
            return jsonify({"message": "You are not a merchant", "status": 403}), 403
        new_product = Products(product_name=name, description=description, price=price, stock=stock, id_merchant=merchant_id)
        session.add(new_product)
        session.commit()
        return jsonify({"message": "Product added successfully", "status": 201, "data": new_product.info_products()}), 201
@products_bp.route("/api/products/mine", methods = ["GET"])
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
    id = get_jwt_identity()
    with Session(bind=db.engine) as session:
        merchant_id = session.scalars(select(Merchants.id).where(Merchants.id_user == id)).first()
        new_product = session.scalars(select(Products).where(Products.id_merchant == merchant_id)).all()
        if new_product:
            return jsonify({"message": "List of yoru products", "status": 200, "data": [p.info_products() for p in new_product]}), 200
        return jsonify({"message": "You don't have any products", "status": 404}), 404

@products_bp.route("/api/products/<int:product_id>", methods = ["PUT"])
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
    id = get_jwt_identity()

    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock")

    # if price is not None or stock is not None: 
    #     if price < 0 or stock < 0 :
    #         return jsonify({"message": "Price and stock cannot be negative", 
    #         "status": 400}), 400
        


    with Session(bind=db.engine) as session:
        merchant_id = session.scalars(select(Merchants.id).where(Merchants.id_user == id)).first()
        product = session.scalars(select(Products).where(Products.id == product_id and Products.id_merchamt == merchant_id)).first()
        if product:
            if "name" in data:
                product.name = name
            if "description" in data:
                product.description = description
            if "price" in data:
                if price > 0:
                    product.price = price
                else:
                    return jsonify({"message": "Price cannot be negative", "status": 400})
            if "stock" in data:
                 if stock > 0:
                    product.stock = stock
                 else:
                    return jsonify({"message": "Stock cannot be negative", "status": 400})
            session.commit()
            return jsonify({"message": "Product updated successfully", "status": 200, "data": product.info_products()}), 200
        return jsonify({"message": "Product not found", "status": 404}), 404

@products_bp.route("/api/products/<int:product_id>", methods = ["DELETE"])
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
    id = get_jwt_identity()
    with Session(bind=db.engine) as session:
        merchant_id = session.scalars(select(Merchants.id).where(Merchants.id_user == id)).first()
        product = session.scalars(select(Products).where(Products.id == product_id  and Products.id_merchant == merchant_id)).first()
        if not product:
            return jsonify({"message": f"You dont have that product", "status": 403}), 403
        session.delete(product)
        session.commit()
        return jsonify({"message": "Product deleted successfully", "status": 200}), 200