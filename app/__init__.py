from os import sendfile

from flask import Flask, send_file, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()  # load biến môi trường từ file .env

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Cấu hình từ file config.py
    app.config.from_object('app.config.Config')

    # Khởi tạo các extension
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'

    # Khởi tạo services
    from app.services.firebase_service import init_firebase
    from app.services.cloudinary_service import init_cloudinary

    init_firebase()
    init_cloudinary()

    # Đăng ký các blueprint
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.payments import payments_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(profile_bp)

    # Đăng ký hàm user_loader cho flask-login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Tạo route trang chủ
    from flask import redirect, url_for

    @app.route('/')
    def index():
        return render_template('home.html')

    return app