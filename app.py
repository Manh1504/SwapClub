from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from models import db, User
from service.user_service import UserService
from service.post_service import PostService
from service.order_service import OrderService


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Create database tables
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        admin = db.session.query(db.exists().where(User.username == 'admin')).scalar()
        if not admin:
            UserService.create_user('admin', 'admin@example.com', 'admin123', is_admin=True)

    # Helper function to check if user is admin
    def is_admin():
        if 'user_id' not in session:
            return False
        user, _ = UserService.get_user_by_id(session['user_id'])
        return user and user.is_admin

    # ========== API ROUTES ==========

    # User API Routes
    @app.route('/api/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Vui lòng điền đầy đủ thông tin"}), 400

        user, error = UserService.create_user(username, email, password)
        if error:
            return jsonify({"error": error}), 400

        return jsonify({"message": "Đăng ký thành công! Vui lòng đăng nhập"}), 201

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Vui lòng điền đầy đủ thông tin"}), 400

        result, error = UserService.authenticate(email, password)
        if error:
            return jsonify({"error": error}), 401

        # Lưu thông tin người dùng vào session
        session['user_id'] = result['user']['id']
        session['username'] = result['user']['username']
        session['email'] = result['user']['email']
        session['is_admin'] = result['user']['is_admin']
        session['token'] = result['token']

        return jsonify({
            "message": "Đăng nhập thành công!",
            "user": result['user'],
            "token": result['token'],
            "redirect": "/admin" if result['user']['is_admin'] else "/main"
        }), 200

    @app.route('/api/logout', methods=['POST'])
    def api_logout():
        session.clear()
        return jsonify({"message": "Đã đăng xuất", "redirect": "/"}), 200

    @app.route('/api/user/profile', methods=['GET'])
    def api_get_user_profile():
        if 'user_id' not in session:
            return jsonify({"error": "Vui lòng đăng nhập"}), 401

        user, error = UserService.get_user_by_id(session['user_id'])
        if error:
            return jsonify({"error": error}), 400

        return jsonify({"user": user.to_dict()}), 200

    # Post API Routes
    @app.route('/api/posts', methods=['GET'])
    def api_get_posts():
        posts = PostService.get_all_posts()
        return jsonify({"posts": posts}), 200

    @app.route('/api/posts', methods=['POST'])
    def api_create_post():
        if 'user_id' not in session:
            return jsonify({"error": "Vui lòng đăng nhập"}), 401

        data = request.get_json()
        product_type = data.get('product_type')
        quantity = data.get('quantity')
        price = data.get('price')
        description = data.get('description', '')
        contact_info = data.get('contact_info')

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            return jsonify({"error": "Số lượng và giá phải là số"}), 400

        if not all([product_type, quantity, price, contact_info]):
            return jsonify({"error": "Vui lòng điền đầy đủ thông tin"}), 400

        post, error = PostService.create_post(
            session['user_id'],
            product_type,
            quantity,
            price,
            description,
            contact_info
        )

        if error:
            return jsonify({"error": error}), 400

        return jsonify({"message": "Đăng bài thành công!", "post": post.to_dict()}), 201

    @app.route('/api/posts/search', methods=['GET'])
    def api_search_posts():
        search_type = request.args.get('type')
        query = request.args.get('query')

        posts = []
        if search_type == 'name' and query:
            posts = PostService.search_posts_by_product_name(query)
        elif search_type == 'price':
            min_price = request.args.get('min_price')
            max_price = request.args.get('max_price')

            try:
                min_price = float(min_price) if min_price else None
                max_price = float(max_price) if max_price else None
                posts = PostService.search_posts_by_price_range(min_price, max_price)
            except ValueError:
                return jsonify({"error": "Giá phải là số"}), 400

        return jsonify({"posts": posts}), 200

    @app.route('/api/posts/<int:post_id>', methods=['GET'])
    def api_get_post(post_id):
        post, error = PostService.get_post_by_id(post_id)
        if error:
            return jsonify({"error": error}), 404

        return jsonify({"post": post.to_dict()}), 200

    # Order API Routes
    @app.route('/api/orders', methods=['POST'])
    def api_create_order():
        if 'user_id' not in session:
            return jsonify({"error": "Vui lòng đăng nhập"}), 401

        data = request.get_json()
        post_id = data.get('post_id')
        quantity = data.get('quantity')

        try:
            post_id = int(post_id)
            quantity = int(quantity)
        except ValueError:
            return jsonify({"error": "Thông tin không hợp lệ"}), 400

        order, error = OrderService.create_order(post_id, session['user_id'], quantity)

        if error:
            return jsonify({"error": error}), 400

        return jsonify({"message": "Đặt hàng thành công!", "order": order.to_dict()}), 201

    @app.route('/api/user/purchases', methods=['GET'])
    def api_get_user_purchases():
        if 'user_id' not in session:
            return jsonify({"error": "Vui lòng đăng nhập"}), 401

        purchases = OrderService.get_orders_by_buyer(session['user_id'])
        return jsonify({"purchases": purchases}), 200

    @app.route('/api/user/sales', methods=['GET'])
    def api_get_user_sales():
        if 'user_id' not in session:
            return jsonify({"error": "Vui lòng đăng nhập"}), 401

        sales = OrderService.get_orders_by_seller(session['user_id'])
        return jsonify({"sales": sales}), 200

    @app.route('/api/user/posts', methods=['GET'])
    def api_get_user_posts():
        if 'user_id' not in session:
            return jsonify({"error": "Vui lòng đăng nhập"}), 401

        posts = PostService.get_posts_by_user(session['user_id'])
        return jsonify({"posts": posts}), 200

    # Admin API Routes
    @app.route('/api/admin/posts', methods=['GET'])
    def api_admin_get_all_posts():
        if not is_admin():
            return jsonify({"error": "Bạn không có quyền truy cập"}), 403

        posts = PostService.get_all_posts()
        return jsonify({"posts": posts}), 200

    @app.route('/api/admin/users', methods=['GET'])
    def api_admin_get_all_users():
        if not is_admin():
            return jsonify({"error": "Bạn không có quyền truy cập"}), 403

        users = UserService.get_all_users()
        return jsonify({"users": users}), 200

    @app.route('/api/admin/orders', methods=['GET'])
    def api_admin_get_all_orders():
        if not is_admin():
            return jsonify({"error": "Bạn không có quyền truy cập"}), 403

        orders = OrderService.get_all_orders()
        return jsonify({"orders": orders}), 200

    @app.route('/api/admin/posts/<int:post_id>', methods=['DELETE'])
    def api_admin_delete_post(post_id):
        if not is_admin():
            return jsonify({"error": "Bạn không có quyền thực hiện hành động này"}), 403

        success, error = PostService.delete_post(post_id)

        if error:
            return jsonify({"error": f"Lỗi khi xóa bài đăng: {error}"}), 400

        return jsonify({"message": "Xóa bài đăng thành công!"}), 200

    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    def api_admin_delete_user(user_id):
        if not is_admin():
            return jsonify({"error": "Bạn không có quyền thực hiện hành động này"}), 403

        # Không cho phép xóa tài khoản admin hiện tại
        if user_id == session.get('user_id'):
            return jsonify({"error": "Không thể xóa tài khoản admin hiện tại"}), 400

        success, error = UserService.delete_user(user_id)

        if error:
            return jsonify({"error": f"Lỗi khi xóa người dùng: {error}"}), 400

        return jsonify({"message": "Xóa người dùng thành công!"}), 200

    # ========== VIEW ROUTES (TEMPLATES) ==========
    # Các route này chỉ trả về template HTML, không có logic xử lý form
    # Tất cả logic xử lý dữ liệu được thực hiện thông qua API endpoints

    @app.route('/')
    def index():
        # Trang chủ - đăng ký, đăng nhập
        return render_template('index.html')

    @app.route('/main')
    def main():
        # Trang chính - hiển thị tất cả bài đăng
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return render_template('main.html', username=session.get('username'))

    @app.route('/payment/<int:post_id>')
    def payment(post_id):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return render_template('payment.html', post_id=post_id, username=session.get('username'))

    @app.route('/user')
    def user_profile():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return render_template('user.html', username=session.get('username'))

    @app.route('/admin')
    def admin_dashboard():
        # Kiểm tra quyền admin
        if not is_admin():
            return redirect(url_for('main'))
        return render_template('admin.html', username=session.get('username'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5050)