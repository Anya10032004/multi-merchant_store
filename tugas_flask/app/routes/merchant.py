from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import  Session
from flask_jwt_extended import  get_jwt, jwt_required, get_jwt_identity
from app import db
from app.models import Merchants, Products


merchants_db = Blueprint("merchants", __name__)

@merchants_db.route("/merchants", methods=["POST"])
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
    id_user = get_jwt_identity() # This for getting the ID from the token that already checked
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
        check2 = session.scalars(select(Merchants).where(Merchants.id_user == id_user)).first()
        if len(checkk) > 0:
            return jsonify({"message": "That store name is already taken", "status": 400}), 400
        if check2:
            return jsonify({"message": "You already have a store", "status": 400}), 400
        new_merchants = Merchants(store_name=store_namee, description=description, id_user=id_user, adress=adress, phone=phone)
        session.add(new_merchants)
        session.commit()
        return jsonify({"message": "Merchants added successfully", "status": 201, "data": new_merchants.info_merchants()}), 201

@merchants_db.route("/merchants/me", methods=["GET"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def get_my_merchant():
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    # Acess the database
    with Session(bind=db.engine) as session:
        id_user = get_jwt_identity() # This for getting the ID from the token that already checked
        merchant = session.scalars(select(Merchants).where(Merchants.id_user == id_user)).first()
        if merchant:
            return jsonify({"message": "Merchant found", "status": 200, "data": merchant.info_merchants()}), 200
        return jsonify({"message": "Merchant not found", "status": 404}), 404
    
@merchants_db.route("/merchants/me", methods  = ["PUT"])
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
        merchant = session.scalars(select(Merchants).where(Merchants.id_user == get_jwt_identity())).first()
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


@merchants_db.route("/merchants", methods  = ["GET"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def get_merchants():
    # Auntetication
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "merchant":
        return jsonify({
            "error": "You have no access because you are not a Merchant"
        })
    # Acess the database
    with Session(bind=db.engine) as session:
        merchants = session.scalars(select(Merchants).order_by(Merchants.id.desc())).all()
        if merchants:
            return jsonify({"message": "Merchant found", "status": 200, "data": [m.info_merchants() for m in merchants]}), 200
        return jsonify({"message": "Merchant not found", "status": 404}), 404
          
@merchants_db.route("/merchants/<int:id>", methods  = ["GET"])
@jwt_required()
def get_merchants_id(id):

    with Session(bind=db.engine) as session:
        merchant = session.execute(select(Merchants.store_name, Products.product_name, Products.price, Products.stock).join(Products, Merchants.id == Products.id_merchant).filter(Merchants.id == id)).all()
        if merchant:
            result = []
            for row in merchant:
                result.append(    {
                    "store_name": row.store_name,
                    "product_name": row.product_name,
                    "price": row.price,
                    "stock": row.stock
                } )
            
            return jsonify({"message": "Store and it's product found", "status": 200, "data": result}), 200
        return jsonify({"message": "Store has no product", "status": 404}), 404    