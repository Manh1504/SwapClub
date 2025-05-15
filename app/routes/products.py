from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.user import User
from app.services.cloudinary_service import upload_image
import os

products_bp = Blueprint('products', __name__, url_prefix='/products')

# Định nghĩa danh sách các danh mục sản phẩm
CATEGORIES = [
    'Điện tử', 'Thời trang', 'Đồ gia dụng', 'Thể thao & Giải trí',
    'Sách & Văn phòng phẩm', 'Đồ trẻ em', 'Khác'
]

# Định nghĩa danh sách các tình trạng sản phẩm
CONDITIONS = [
    'Mới', 'Như mới (99%)', 'Tốt (95-98%)', 'Khá tốt (90-94%)',
    'Đã qua sử dụng (70-89%)', 'Cũ (dưới 70%)'
]


@products_bp.route('/')
def list():
    # Lấy tham số từ query string
    category = request.args.get('category')
    status = request.args.get('status', 'available')  # Mặc định chỉ hiển thị sản phẩm còn hàng

    # Lấy danh sách sản phẩm
    products = Product.get_all(limit=50, status=status, category=category)

    return render_template('products/list.html',
                           products=products,
                           categories=CATEGORIES,
                           current_category=category)


@products_bp.route('/<product_id>')
def detail(product_id):
    # Lấy thông tin sản phẩm
    product = Product.get_by_id(product_id)

    if not product:
        abort(404)

    # Lấy thông tin người bán
    seller = User.get_by_id(product.seller_id)

    return render_template('products/detail.html', product=product, seller=seller)


@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        condition = request.form.get('condition')
        category = request.form.get('category')

        # Kiểm tra dữ liệu đầu vào
        if not title or not description or price <= 0 or not condition or not category:
            flash('Vui lòng điền đầy đủ thông tin sản phẩm', 'danger')
            return render_template('products/create.html',
                                   categories=CATEGORIES,
                                   conditions=CONDITIONS)

        # Xử lý upload ảnh
        images = []
        for i in range(5):  # Cho phép tối đa 5 ảnh
            image_file = request.files.get(f'image{i}')
            if image_file and image_file.filename:
                image_info = upload_image(image_file, folder=f"products/{current_user.id}")
                if image_info:
                    images.append(image_info)

        # Tạo sản phẩm mới
        product = Product(
            title=title,
            description=description,
            price=price,
            condition=condition,
            category=category,
            seller_id=current_user.id,
            images=images,
            status="available"
        )

        if product.save():
            flash('Đăng bài thành công!', 'success')
            return redirect(url_for('products.detail', product_id=product.id))
        else:
            flash('Đăng bài thất bại. Vui lòng thử lại.', 'danger')

    return render_template('products/create.html',
                           categories=CATEGORIES,
                           conditions=CONDITIONS)


@products_bp.route('/<product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    # Lấy thông tin sản phẩm
    product = Product.get_by_id(product_id)

    if not product:
        abort(404)

    # Kiểm tra quyền chỉnh sửa
    if product.seller_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        condition = request.form.get('condition')
        category = request.form.get('category')

        # Kiểm tra dữ liệu đầu vào
        if not title or not description or price <= 0 or not condition or not category:
            flash('Vui lòng điền đầy đủ thông tin sản phẩm', 'danger')
            return render_template('products/edit.html',
                                   product=product,
                                   categories=CATEGORIES,
                                   conditions=CONDITIONS)

        # Cập nhật thông tin sản phẩm
        product.title = title
        product.description = description
        product.price = price
        product.condition = condition
        product.category = category

        # Xử lý upload ảnh mới (nếu có)
        for i in range(5):  # Cho phép tối đa 5 ảnh
            image_file = request.files.get(f'image{i}')
            if image_file and image_file.filename:
                image_info = upload_image(image_file, folder=f"products/{current_user.id}")
                if image_info:
                    product.images.append(image_info)

        if product.save():
            flash('Cập nhật sản phẩm thành công!', 'success')
            return redirect(url_for('products.detail', product_id=product.id))
        else:
            flash('Cập nhật sản phẩm thất bại. Vui lòng thử lại.', 'danger')

    return render_template('products/edit.html',
                           product=product,
                           categories=CATEGORIES,
                           conditions=CONDITIONS)


@products_bp.route('/<product_id>/delete', methods=['POST'])
@login_required
def delete(product_id):
    # Lấy thông tin sản phẩm
    product = Product.get_by_id(product_id)

    if not product:
        abort(404)

    # Kiểm tra quyền xóa
    if product.seller_id != current_user.id:
        abort(403)

    # Cập nhật trạng thái thành đã xóa (không xóa hoàn toàn)
    if product.update_status('deleted'):
        flash('Xóa sản phẩm thành công!', 'success')
    else:
        flash('Xóa sản phẩm thất bại. Vui lòng thử lại.', 'danger')

    return redirect(url_for('profile.posted_products'))