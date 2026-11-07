from flask import Blueprint, Flask, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import Session
from sqlalchemy import  select
from app import db
from app.models import Users

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
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
    
    # Acess the database
    with Session(bind=db.engine) as session:
        # check if email already exists
        user = session.scalars(select(Users).where(Users.email == emaill)).first()
        if user:
            return jsonify({"message": "Email already exists", "status": 400}), 400
        new_users = Users(name=namee, email=emaill, password=hash_password, role=rolee)
        session.add(new_users)
        session.commit()
        return jsonify({"message": "User added successfully", "status": 201, "data": new_users.info_users()}), 201


@auth_bp.route("/login", methods=["POST"])
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