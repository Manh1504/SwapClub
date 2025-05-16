from flask import Blueprint, request, jsonify
from service.post_service import PostService
from flask_jwt_extended import jwt_required, get_jwt_identity

post_bp = Blueprint('post', __name__, url_prefix='/api/posts')


@post_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    product_type = data.get('product_type')
    quantity = data.get('quantity')
    price = data.get('price')
    description = data.get('description', '')
    contact_info = data.get('contact_info')

    if not all([product_type, quantity, price, contact_info]):
        return jsonify({"error": "Missing required fields"}), 400

    post, error = PostService.create_post(
        current_user_id,
        product_type,
        quantity,
        price,
        description,
        contact_info
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Post created successfully", "post": post.to_dict()}), 201


@post_bp.route('/', methods=['GET'])
def get_all_posts():
    posts = PostService.get_all_posts()
    return jsonify({"posts": posts}), 200


@post_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_posts():
    current_user_id = get_jwt_identity()
    posts = PostService.get_posts_by_user(current_user_id)
    return jsonify({"posts": posts}), 200


@post_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post, error = PostService.get_post_by_id(post_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"post": post.to_dict()}), 200


@post_bp.route('/search/name', methods=['GET'])
def search_by_name():
    product_name = request.args.get('name', '')
    posts = PostService.search_posts_by_product_name(product_name)
    return jsonify({"posts": posts}), 200


@post_bp.route('/search/price', methods=['GET'])
def search_by_price():
    min_price = request.args.get('min')
    max_price = request.args.get('max')

    # Convert to float if not None
    min_price = float(min_price) if min_price else None
    max_price = float(max_price) if max_price else None

    posts = PostService.search_posts_by_price_range(min_price, max_price)
    return jsonify({"posts": posts}), 200