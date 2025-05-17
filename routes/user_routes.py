from flask import Blueprint, request, jsonify
from service.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    user, error = UserService.create_user(username, email, password)
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


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    # Kiểm tra nếu user hiện tại là admin
    current_user_id = get_jwt_identity()
    user, error = UserService.get_user_by_id(current_user_id)

    if error or not user or not user.is_admin:
        return jsonify({"error": "Unauthorized access"}), 403

    users = UserService.get_all_users()
    return jsonify({"users": users}), 200


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # Kiểm tra nếu user hiện tại là admin
    current_user_id = get_jwt_identity()
    user, error = UserService.get_user_by_id(current_user_id)

    if error or not user or not user.is_admin:
        return jsonify({"error": "Unauthorized access"}), 403

    # Không cho phép xóa chính mình
    if user_id == current_user_id:
        return jsonify({"error": "Cannot delete your own account"}), 400

    success, error = UserService.delete_user(user_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User deleted successfully"}), 200