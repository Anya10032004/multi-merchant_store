from flask import Flask
from flask_jwt_extended import JWTManager 
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from app.errors import register_error_handlers

from app.routes.auth import auth_bp
from app.routes.merchants import merchants_bp
from app.routes.products import products_bp
from app.routes.catalog import catalog_bp
from app.routes.claims import claims_bp

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class = Config): # create_app() function is used to changes on flask application
    app_toko =  Flask(__name__) # Making the Flask app 
    app_toko.config.from_object(config_class) #After initialize the flask app above, we set up configuration

    db.init_app(app_toko) # Initialize database
    jwt.init_app(app_toko)

    app_toko.register_blueprint(auth_bp, url_prefix="/api")
    app_toko.register_blueprint(merchants_bp, url_prefix="/api")
    app_toko.register_blueprint(products_bp, url_prefix="/api")
    app_toko.register_blueprint(catalog_bp, url_prefix="/api")
    app_toko.register_blueprint(claims_bp, url_prefix="/api")


    register_error_handlers(app_toko)

    return app_toko

    