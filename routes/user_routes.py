from flask import Blueprint, request, jsonify
from service.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user, error = UserService.create_user(username, password)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User created successfully", "user": user.to_dict()}), 201


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    result, error = UserService.authenticate(username, password)
    if error:
        return jsonify({"error": error}), 401

    return jsonify(result), 200


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user, error = UserService.get_user_by_id(current_user_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"user": user.to_dict()}), 200
