from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.order import Order
from app.models.user import User

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@login_required
def index():
    """Hiển thị trang hồ sơ cá nhân"""
    return render_template('profile/index.html', user=current_user)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Chỉnh sửa thông tin hồ sơ cá nhân"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if current_user.update(name=name, phone=phone, address=address):
            flash('Cập nhật thông tin cá nhân thành công!', 'success')
        else:
            flash('Cập nhật thông tin cá nhân thất bại. Vui lòng thử lại.', 'danger')

        return redirect(url_for('profile.index'))

    return render_template('profile/edit.html', user=current_user)


@profile_bp.route('/products')
@login_required
def posted_products():
    """Hiển thị danh sách sản phẩm đã đăng"""
    # Lấy tham số trạng thái từ query string (mặc định là không lấy sản phẩm đã xóa)
    status = request.args.get('status')

    if status:
        products = Product.get_all(seller_id=current_user.id, status=status)
    else:
        # Lấy tất cả sản phẩm trừ các sản phẩm đã xóa
        products = []
        for product in Product.get_all(seller_id=current_user.id):
            if product.status != 'deleted':
                products.append(product)

    return render_template('profile/posted_products.html', products=products)


@profile_bp.route('/purchases')
@login_required
def purchase_history():
    """Hiển thị lịch sử mua hàng"""
    orders = Order.get_by_buyer(current_user.id)

    # Lấy thông tin sản phẩm cho mỗi đơn hàng
    for order in orders:
        order.product = Product.get_by_id(order.product_id)
        order.seller = User.get_by_id(order.seller_id)

    return render_template('profile/purchase_history.html', orders=orders)


@profile_bp.route('/sales')
@login_required
def sales_history():
    """Hiển thị lịch sử bán hàng"""
    orders = Order.get_by_seller(current_user.id)

    # Lấy thông tin sản phẩm và người mua cho mỗi đơn hàng
    for order in orders:
        order.product = Product.get_by_id(order.product_id)
        order.buyer = User.get_by_id(order.buyer_id)

    return render_template('profile/sales_history.html', orders=orders)