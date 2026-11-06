from app import create_app, db
import json 
from flask import Flask, jsonify,request

app_store = create_app() # This is for starting the store app

@app_store.route("/api", methods=["GET"])
def main():
    return jsonify({
        "message": "Welcome to the API",
        "status": 200,
        "data": None
    })

if __name__ == "__main__":

    with app_store.app_context():
        db.create_all()     
    
    app_store.run(debug=True) # This is for starting the store app
    
