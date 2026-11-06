from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

merchants_bp = Blueprint("merchants", __name__)
