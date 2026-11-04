from flask import Flask, jsonify
from .app.config import DevelopementConfig
from .app.models import db
from .app.error import register_error_handlers
from .app.Route.notes import notes_bp

def create_app(config_class = DevelopementConfig): # create_app() function is used to changes on flask application
    app_toko =  Flask(__name__) # Making the Flask app 
    app_toko.config.from_object(config_class) #After initialize the flask app above, we set up configuration

    db.init_app(app_toko) # Initialize database
    app_toko.register_blueprint(notes_bp) # Initialize the table in the database
    register_error_handlers(app_toko) # Initiakize error handlers

    @app_toko.route("/api", methods=["GET"])
    def main():
        return jsonify({
        "message": "Welcome to the API",
        "status": 200,
        "data": None
        })
    
    # Create the tables
    with app_toko.app_context():
        db.create_all()
    
    return app_toko

    