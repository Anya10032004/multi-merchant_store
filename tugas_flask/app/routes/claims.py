from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import  Session
from flask_jwt_extended import  get_jwt, jwt_required, get_jwt_identity
from app import db
from app.models import Merchants, Products, Claims

claims_bp = Blueprint("claims", __name__)

@claims_bp.route("/claims", methods = ["POST"])
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
    product_id = data.get("id_product")
    amount = data.get("quantity")
    if product_id is None or amount is None:
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
        new_claim = Claims(id_product=product_id, quantity=amount, id_user=token_acess.get("id"))
        session.add(new_claim)
        session.commit()
        return jsonify({"message": "Claim added successfully", "status": 201, "data": new_claim.info_claims()}), 201

@claims_bp.route("/claims", methods = ["GET"])
@jwt_required() # This is means that to  acess this endpoint you need to login first (we need to bring the token when accessing this endpoint)
def get_claims():
    token_acess = get_jwt() # After we use jwt_required() to check if we have login, we 
                            # will use get_jwt() to get the token that has already checked
    rolee = token_acess.get("role")
    if rolee.lower() != "user":
        return jsonify({
            "error": "You have no access because you are not a User"
        })
    with Session(bind=db.engine) as session:
        claims = session.scalars(select(Claims).order_by(Claims.id.desc())).all()
        if claims:
            return jsonify({"message": "List of claims", "status": 200, "data": [c.info_claims() for c in claims]}), 200
        return jsonify({"message": "No claims found", "status": 404}), 404