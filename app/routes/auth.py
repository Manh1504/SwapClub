from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.services.firebase_service import get_firebase_auth
from werkzeug.security import generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('products.list'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # Kiểm tra xác nhận mật khẩu
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp', 'danger')
            return render_template('auth/register.html')

        # Kiểm tra email đã tồn tại chưa
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email đã được sử dụng', 'danger')
            return render_template('auth/register.html')

        try:
            # Tạo người dùng mới
            user = User.create(email, password, name, phone, address)

            if user:
                # Đăng nhập người dùng sau khi đăng ký thành công
                login_user(user)
                flash('Đăng ký tài khoản thành công!', 'success')
                return redirect(url_for('products.list'))
            else:
                flash('Đăng ký thất bại. Vui lòng thử lại.', 'danger')
        except Exception as e:
            flash(f'Lỗi: {str(e)}', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products.list'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Đăng nhập với Firebase Auth
            auth = get_firebase_auth()
            user_auth = auth.sign_in_with_email_and_password(email, password)

            # Lấy thông tin người dùng từ Firestore
            user = User.get_by_id(user_auth['localId'])

            if user:
                login_user(user)
                flash('Đăng nhập thành công!', 'success')

                # Chuyển hướng đến trang được yêu cầu (nếu có)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('products.list'))
            else:
                flash('Không tìm thấy thông tin người dùng', 'danger')
        except Exception as e:
            flash('Email hoặc mật khẩu không chính xác', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if current_user.update(name, phone, address):
            flash('Cập nhật thông tin thành công!', 'success')
        else:
            flash('Cập nhật thông tin thất bại', 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')