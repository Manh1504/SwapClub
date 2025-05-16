from flask import Blueprint, request, jsonify
from service.order_service import OrderService
from flask_jwt_extended import jwt_required, get_jwt_identity

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