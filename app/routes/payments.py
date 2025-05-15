from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.models.payment import PaymentService
from app.models.order import Order
import json

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


@payments_bp.route('/methods')
def methods():
    """Hiển thị danh sách phương thức thanh toán"""
    payment_methods = PaymentService.get_payment_methods()
    return render_template('payments/methods.html', payment_methods=payment_methods)


@payments_bp.route('/process/<order_id>', methods=['GET', 'POST'])
@login_required
def process(order_id):
    """Xử lý thanh toán cho đơn hàng"""
    order = Order.get_by_id(order_id)

    if not order:
        abort(404)

    # Chỉ người mua có thể thanh toán đơn hàng
    if order.buyer_id != current_user.id:
        abort(403)

    # Kiểm tra xem đơn hàng đã được thanh toán chưa
    if order.payment_status == 'paid':
        flash('Đơn hàng này đã được thanh toán', 'info')
        return redirect(url_for('orders.detail', order_id=order_id))

    if request.method == 'POST':
        payment_method = order.payment_method

        # Tạo yêu cầu thanh toán
        payment = PaymentService.create_payment(
            order_id=order.id,
            amount=order.price,
            payment_method=payment_method,
            details={
                'buyer_id': order.buyer_id,
                'seller_id': order.seller_id
            }
        )

        # Xử lý từng phương thức thanh toán
        if payment_method == 'cash':
            # Thanh toán COD - không cần xử lý gì thêm
            flash('Đơn hàng sẽ được thanh toán khi nhận hàng', 'success')
            return redirect(url_for('orders.detail', order_id=order_id))

        elif payment_method == 'bank_transfer':
            # Hiển thị thông tin chuyển khoản
            return render_template('payments/bank_transfer.html', order=order, payment=payment)

        elif payment_method == 'credit_card':
            # Xử lý thanh toán thẻ tín dụng
            payment_details = {
                'card_number': request.form.get('card_number'),
                'card_holder': request.form.get('card_holder'),
                'expiry_date': request.form.get('expiry_date'),
                'cvv': request.form.get('cvv')
            }

            # Trong môi trường thực tế, gọi API của cổng thanh toán ở đây
            # Giả lập xử lý thanh toán thành công
            result = PaymentService.process_payment(payment['id'], payment_details)

            if result['status'] == 'paid':
                # Cập nhật trạng thái thanh toán của đơn hàng
                order.update_payment_status('paid')
                flash('Thanh toán thành công!', 'success')
                return redirect(url_for('orders.detail', order_id=order_id))
            else:
                flash('Thanh toán thất bại. Vui lòng thử lại.', 'danger')

        else:
            flash('Phương thức thanh toán không hợp lệ', 'danger')

    # Hiển thị form thanh toán tương ứng với phương thức thanh toán đã chọn
    return render_template('payments/process.html', order=order)


@payments_bp.route('/confirm/<order_id>', methods=['POST'])
@login_required
def confirm(order_id):
    """Xác nhận đã thanh toán (cho bank_transfer)"""
    order = Order.get_by_id(order_id)

    if not order:
        abort(404)

    # Chỉ người mua có thể xác nhận thanh toán
    if order.buyer_id != current_user.id:
        abort(403)

    # Cập nhật trạng thái thanh toán
    if order.update_payment_status('pending_verification'):
        flash('Xác nhận thanh toán thành công. Chúng tôi sẽ kiểm tra và cập nhật trong thời gian sớm nhất.', 'success')
    else:
        flash('Xác nhận thanh toán thất bại. Vui lòng thử lại.', 'danger')

    return redirect(url_for('orders.detail', order_id=order_id))


@payments_bp.route('/verify/<order_id>', methods=['POST'])
@login_required
def verify(order_id):
    """Xác minh thanh toán (cho người bán)"""
    order = Order.get_by_id(order_id)

    if not order:
        abort(404)

    # Chỉ người bán có thể xác minh thanh toán
    if order.seller_id != current_user.id:
        abort(403)

    verified = request.form.get('verified') == 'true'

    if verified:
        # Cập nhật trạng thái thanh toán thành công
        if order.update_payment_status('paid'):
            flash('Xác minh thanh toán thành công', 'success')
        else:
            flash('Xác minh thanh toán thất bại. Vui lòng thử lại.', 'danger')
    else:
        # Cập nhật trạng thái thanh toán thất bại
        if order.update_payment_status('failed'):
            flash('Đã đánh dấu thanh toán là thất bại', 'warning')
        else:
            flash('Cập nhật trạng thái thanh toán thất bại. Vui lòng thử lại.', 'danger')

    return redirect(url_for('orders.detail', order_id=order_id))