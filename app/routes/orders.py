from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.models.payment import PaymentService

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


@orders_bp.route('/')
@login_required
def list():
    """Hiển thị danh sách đơn hàng của người dùng hiện tại"""
    orders = Order.get_by_buyer(current_user.id)

    # Lấy thông tin sản phẩm cho mỗi đơn hàng
    for order in orders:
        order.product = Product.get_by_id(order.product_id)

    return render_template('orders/list.html', orders=orders)


@orders_bp.route('/<order_id>')
@login_required
def detail(order_id):
    """Hiển thị chi tiết đơn hàng"""
    order = Order.get_by_id(order_id)

    if not order:
        abort(404)

    # Kiểm tra quyền truy cập
    if order.buyer_id != current_user.id and order.seller_id != current_user.id:
        abort(403)

    # Lấy thông tin sản phẩm
    product = Product.get_by_id(order.product_id)

    # Lấy thông tin người bán và người mua
    buyer = User.get_by_id(order.buyer_id)
    seller = User.get_by_id(order.seller_id)

    return render_template('orders/detail.html', order=order, product=product, buyer=buyer, seller=seller)


@orders_bp.route('/create/<product_id>', methods=['GET', 'POST'])
@login_required
def create(product_id):
    """Tạo đơn hàng mới"""
    product = Product.get_by_id(product_id)

    if not product:
        abort(404)

    # Kiểm tra xem sản phẩm có còn khả dụng không
    if product.status != 'available':
        flash('Sản phẩm này hiện không còn khả dụng để mua', 'danger')
        return redirect(url_for('products.detail', product_id=product_id))

    # Kiểm tra người dùng không mua sản phẩm của chính họ
    if product.seller_id == current_user.id:
        flash('Bạn không thể mua sản phẩm của chính mình', 'danger')
        return redirect(url_for('products.detail', product_id=product_id))

    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        payment_method = request.form.get('payment_method')

        if not shipping_address:
            flash('Vui lòng nhập địa chỉ giao hàng', 'danger')
            return render_template('orders/checkout.html', product=product,
                                   payment_methods=PaymentService.get_payment_methods())

        # Tạo đơn hàng mới
        order = Order(
            product_id=product.id,
            buyer_id=current_user.id,
            seller_id=product.seller_id,
            price=product.price,
            status='pending',
            shipping_address=shipping_address,
            payment_method=payment_method,
            payment_status='pending'
        )

        if order.save():
            # Cập nhật trạng thái sản phẩm thành 'pending'
            product.update_status('pending')

            flash('Đặt hàng thành công!', 'success')
            return redirect(url_for('orders.confirmation', order_id=order.id))
        else:
            flash('Đặt hàng thất bại. Vui lòng thử lại.', 'danger')

    # Lấy thông tin địa chỉ người dùng (nếu có)
    shipping_address = current_user.address or ''

    return render_template('orders/checkout.html',
                           product=product,
                           shipping_address=shipping_address,
                           payment_methods=PaymentService.get_payment_methods())


@orders_bp.route('/confirmation/<order_id>')
@login_required
def confirmation(order_id):
    """Hiển thị trang xác nhận đơn hàng"""
    order = Order.get_by_id(order_id)

    if not order or order.buyer_id != current_user.id:
        abort(404)

    product = Product.get_by_id(order.product_id)
    seller = User.get_by_id(order.seller_id)

    return render_template('orders/confirmation.html', order=order, product=product, seller=seller)


@orders_bp.route('/<order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    """Hủy đơn hàng"""
    order = Order.get_by_id(order_id)

    if not order:
        abort(404)

    # Chỉ người mua có thể hủy đơn hàng
    if order.buyer_id != current_user.id:
        abort(403)

    # Chỉ có thể hủy đơn hàng ở trạng thái 'pending'
    if order.status != 'pending':
        flash('Không thể hủy đơn hàng này vì đã được xử lý', 'danger')
        return redirect(url_for('orders.detail', order_id=order_id))

    # Cập nhật trạng thái đơn hàng
    if order.update_status('cancelled'):
        # Cập nhật trạng thái sản phẩm trở lại 'available'
        product = Product.get_by_id(order.product_id)
        if product:
            product.update_status('available')

        flash('Hủy đơn hàng thành công', 'success')
    else:
        flash('Hủy đơn hàng thất bại. Vui lòng thử lại.', 'danger')

    return redirect(url_for('orders.list'))


@orders_bp.route('/<order_id>/update-status', methods=['POST'])
@login_required
def update_status(order_id):
    """Cập nhật trạng thái đơn hàng (dành cho người bán)"""
    order = Order.get_by_id(order_id)

    if not order:
        abort(404)

    # Chỉ người bán có thể cập nhật trạng thái đơn hàng
    if order.seller_id != current_user.id:
        abort(403)

    status = request.form.get('status')
    valid_statuses = ['confirmed', 'shipped', 'delivered', 'cancelled']

    if status not in valid_statuses:
        flash('Trạng thái không hợp lệ', 'danger')
        return redirect(url_for('orders.detail', order_id=order_id))

    # Cập nhật trạng thái đơn hàng
    if order.update_status(status):
        # Nếu người bán hủy đơn hàng, cập nhật trạng thái sản phẩm trở lại 'available'
        if status == 'cancelled':
            product = Product.get_by_id(order.product_id)
            if product:
                product.update_status('available')

        # Nếu đơn hàng đã giao thành công, cập nhật trạng thái sản phẩm thành 'sold'
        elif status == 'delivered':
            product = Product.get_by_id(order.product_id)
            if product:
                product.update_status('sold')

        flash(f'Cập nhật trạng thái đơn hàng thành "{status}" thành công', 'success')
    else:
        flash('Cập nhật trạng thái đơn hàng thất bại. Vui lòng thử lại.', 'danger')

    return redirect(url_for('orders.detail', order_id=order_id))