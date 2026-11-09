from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import  Session
from flask_jwt_extended import  get_jwt, jwt_required, get_jwt_identity
from app import db
from app.models import Merchants, Products


catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.route("/catalog", methods = ["GET"])    
def catalog():
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type =int)
    search = request.args.get('search')
    id_merchant = request.args.get("merchant_id", type=int)


    with Session(bind=db.engine) as session:
        products = select(Products.product_name, Merchants.store_name, Products.stock).join(Merchants, Products.id_merchant == Merchants.id)
            
        if search is not None:
            products = products.where(Products.product_name.ilike(f"%{search}%"))
        
        if id_merchant is not None:
            products = products.where(Products.id_merchant == id_merchant)
        
        if page is not None and per_page is not None:
            if page <= 0:
                return jsonify({
                    "message": "0 is not allow",
                    "status": 404
                })
            products = products.limit(per_page).offset((page-1)*per_page  + 1)

        products = session.execute(products).all()
        if len(products) == 0:
            return jsonify({"message": "No products found", "status": 404}), 404 


        return jsonify(
                             {
                              "message": "List of products", "status": 200, 
                             "data": [
                                {
                                "Product name": p.product_name, 
                                "Store name": p.store_name, 
                                "stock": p.stock } for p in products if int(p.stock) > 0
                                ] 
                                }

                                ), 200




@catalog_bp.route("/catalog/<int:product_id>", methods = ["GET"])
def get_catalog(product_id):
    with Session(bind=db.engine) as session:
        product = session.scalars(select(Products).where(Products.id == product_id)).all()
        if product:
            return jsonify({"message": "Product found", "status": 200, "data": [l.info_products() for l in product]}), 200
        return jsonify({"message": "Product not found", "status": 404}), 404