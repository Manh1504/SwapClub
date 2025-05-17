from flask import Blueprint, request, jsonify
from service.order_service import OrderService
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.user_service import UserService
from service.post_service import PostService

order_bp = Blueprint('order', __name__, url_prefix='/api/orders')


@order_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    post_id = data.get('post_id')
    quantity = data.get('quantity')

    if not post_id or not quantity:
        return jsonify({"error": "Post ID and quantity are required"}), 400

    try:
        post_id = int(post_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"error": "Post ID and quantity must be integers"}), 400

    order, error = OrderService.create_order(post_id, current_user_id, quantity)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Order placed successfully", "order": order.to_dict()}), 201


@order_bp.route('/purchases', methods=['GET'])
@jwt_required()
def get_purchases():
    current_user_id = get_jwt_identity()
    orders = OrderService.get_orders_by_buyer(current_user_id)
    return jsonify({"purchases": orders}), 200


@order_bp.route('/sales', methods=['GET'])
@jwt_required()
def get_sales():
    current_user_id = get_jwt_identity()
    orders = OrderService.get_orders_by_seller(current_user_id)
    return jsonify({"sales": orders}), 200


@order_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_orders():
    # Kiểm tra quyền admin trước khi cho phép xem tất cả đơn hàng
    current_user_id = get_jwt_identity()
    user, error = UserService.get_user_by_id(current_user_id)

    if error or not user or not user.is_admin:
        return jsonify({"error": "Unauthorized access"}), 403

    orders = OrderService.get_all_orders()
    return jsonify({"orders": orders}), 200


@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    current_user_id = get_jwt_identity()

    # Lấy thông tin đơn hàng từ database
    # (Giả định có phương thức này trong OrderService)
    order = OrderService.get_order_by_id(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Kiểm tra quyền truy cập: admin, người mua hoặc người bán
    user, error = UserService.get_user_by_id(current_user_id)
    if error:
        return jsonify({"error": error}), 404

    if not user.is_admin and order.get('buyer_id') != current_user_id and order.get('seller_id') != current_user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    return jsonify({"order": order}), 200