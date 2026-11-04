from flask import Blueprint, request, jsonify
from .models import db, note
from ..validators import validate_function

