from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from models import db, User
from routes.user_routes import user_bp
from routes.post_routes import post_bp
from routes.order_routes import order_bp
from service.user_service import UserService
from service.post_service import PostService
from service.order_service import OrderService


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints for API
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(order_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        admin = db.session.query(db.exists().where(User.username == 'admin')).scalar()
        if not admin:
            UserService.create_user('admin', 'admin123', is_admin=True)

    # Helper function to check if user is admin
    def is_admin():
        if 'user_id' not in session:
            return False
        user, _ = UserService.get_user_by_id(session['user_id'])
        return user and user.is_admin

    # Web routes using templates
    @app.route('/')
    def index():
        # Trang chủ - đăng ký, đăng nhập
        return render_template('index.html')

    @app.route('/register', methods=['POST'])
    def register():
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Vui lòng điền đầy đủ thông tin', 'error')
            return redirect(url_for('index'))

        user, error = UserService.create_user(username, password)
        if error:
            flash(error, 'error')
            return redirect(url_for('index'))

        flash('Đăng ký thành công! Vui lòng đăng nhập', 'success')
        return redirect(url_for('index'))

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Vui lòng điền đầy đủ thông tin', 'error')
            return redirect(url_for('index'))

        result, error = UserService.authenticate(username, password)
        if error:
            flash(error, 'error')
            return redirect(url_for('index'))

        # Lưu thông tin người dùng và token vào session
        session['user_id'] = result['user']['id']
        session['username'] = result['user']['username']
        session['is_admin'] = result['user']['is_admin']
        session['token'] = result['token']

        flash('Đăng nhập thành công!', 'success')

        # Chuyển hướng đến trang admin nếu là admin
        if result['user']['is_admin']:
            return redirect(url_for('admin_dashboard'))

        return redirect(url_for('main'))

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Đã đăng xuất', 'info')
        return redirect(url_for('index'))

    @app.route('/main')
    def main():
        # Trang chính - hiển thị tất cả bài đăng và form đăng bài mới
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập', 'error')
            return redirect(url_for('index'))

        # Lấy danh sách bài đăng
        posts = PostService.get_all_posts()
        return render_template('main.html', posts=posts, username=session.get('username'))

    @app.route('/post/create', methods=['POST'])
    def create_post():
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập', 'error')
            return redirect(url_for('index'))

        product_type = request.form.get('product_type')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        description = request.form.get('description', '')
        contact_info = request.form.get('contact_info')

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            flash('Số lượng và giá phải là số', 'error')
            return redirect(url_for('main'))

        if not all([product_type, quantity, price, contact_info]):
            flash('Vui lòng điền đầy đủ thông tin', 'error')
            return redirect(url_for('main'))

        post, error = PostService.create_post(
            session['user_id'],
            product_type,
            quantity,
            price,
            description,
            contact_info
        )

        if error:
            flash(error, 'error')
        else:
            flash('Đăng bài thành công!', 'success')

        return redirect(url_for('main'))

    @app.route('/search')
    def search():
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
                flash('Giá phải là số', 'error')
                return redirect(url_for('main'))

        return render_template('main.html', posts=posts, username=session.get('username'), search=True)

    @app.route('/payment/<int:post_id>')
    def payment(post_id):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập', 'error')
            return redirect(url_for('index'))

        post, error = PostService.get_post_by_id(post_id)
        if error:
            flash(error, 'error')
            return redirect(url_for('main'))

        return render_template('payment.html', post=post.to_dict(), username=session.get('username'))

    @app.route('/order/create', methods=['POST'])
    def create_order():
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập', 'error')
            return redirect(url_for('index'))

        post_id = request.form.get('post_id')
        quantity = request.form.get('quantity')

        try:
            post_id = int(post_id)
            quantity = int(quantity)
        except ValueError:
            flash('Thông tin không hợp lệ', 'error')
            return redirect(url_for('main'))

        order, error = OrderService.create_order(post_id, session['user_id'], quantity)

        if error:
            flash(error, 'error')
            return redirect(url_for('payment', post_id=post_id))

        flash('Đặt hàng thành công!', 'success')
        return redirect(url_for('user_profile'))

    @app.route('/user')
    def user_profile():
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập', 'error')
            return redirect(url_for('index'))

        # Lấy thông tin người dùng
        user, _ = UserService.get_user_by_id(session['user_id'])

        # Lấy lịch sử đăng bài
        posts = PostService.get_posts_by_user(session['user_id'])

        # Lấy lịch sử mua hàng
        purchases = OrderService.get_orders_by_buyer(session['user_id'])

        # Lấy lịch sử bán hàng
        sales = OrderService.get_orders_by_seller(session['user_id'])

        return render_template(
            'user.html',
            username=session.get('username'),
            posts=posts,
            purchases=purchases,
            sales=sales
        )

    # Admin routes
    @app.route('/admin')
    def admin_dashboard():
        # Kiểm tra quyền admin
        if not is_admin():
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('main'))

        # Lấy tất cả bài đăng
        all_posts = PostService.get_all_posts()

        # Lấy tất cả người dùng
        all_users = UserService.get_all_users()

        # Lấy tất cả đơn hàng
        all_orders = OrderService.get_all_orders()

        return render_template(
            'admin.html',
            username=session.get('username'),
            posts=all_posts,
            users=all_users,
            orders=all_orders
        )

    @app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
    def admin_delete_post(post_id):
        # Kiểm tra quyền admin
        if not is_admin():
            flash('Bạn không có quyền thực hiện hành động này', 'error')
            return redirect(url_for('main'))

        success, error = PostService.delete_post(post_id)

        if error:
            flash(f'Lỗi khi xóa bài đăng: {error}', 'error')
        else:
            flash('Xóa bài đăng thành công!', 'success')

        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
    def admin_delete_user(user_id):
        # Kiểm tra quyền admin
        if not is_admin():
            flash('Bạn không có quyền thực hiện hành động này', 'error')
            return redirect(url_for('main'))

        # Không cho phép xóa tài khoản admin hiện tại
        if user_id == session['user_id']:
            flash('Không thể xóa tài khoản admin hiện tại', 'error')
            return redirect(url_for('admin_dashboard'))

        success, error = UserService.delete_user(user_id)

        if error:
            flash(f'Lỗi khi xóa người dùng: {error}', 'error')
        else:
            flash('Xóa người dùng thành công!', 'success')

        return redirect(url_for('admin_dashboard'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5050)