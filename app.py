from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

load_dotenv()  # Load biến môi trường từ .env
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
CORS(app)

# Khởi tạo Firebase Admin SDK
cred = credentials.Certificate('swap.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


# Middleware kiểm tra xác thực
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'uid' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)

    return decorated_function


# Route hiển thị trang
@app.route('/')
@app.route('/login')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('main.html')


@app.route('/payment')
def payment():
    return render_template('payment.html')


@app.route('/user')
def user_profile():
    return render_template('user.html')


# API endpoints
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    try:
        # Tạo người dùng mới trong Firebase Authentication
        user = auth.create_user(
            email=data['email'],
            password=data['password'],
            display_name=data['username']
        )

        # Lưu thông tin người dùng vào Firestore
        db.collection('users').document(user.uid).set({
            'username': data['username'],
            'email': data['email'],
            'created_at': firestore.SERVER_TIMESTAMP,
            'phone': '',
            'address': '',
            'purchases': [],
            'sales': [],
            'favorites': []
        })

        # Thiết lập phiên đăng nhập
        session['uid'] = user.uid
        session['username'] = data['username']

        return jsonify({'success': True, 'uid': user.uid}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        # Xác thực người dùng thông qua Firebase Authentication
        # Trong môi trường thực tế, sử dụng Firebase Auth REST API hoặc Firebase Admin SDK
        # để xác thực. Dưới đây là ví dụ đơn giản:

        # Giả định: Đây là cách thủ công để demo logic
        # Trong thực tế, bạn nên sử dụng Firebase Auth REST API
        user_docs = db.collection('users').where('email', '==', data['email']).limit(1).get()

        if not user_docs:
            return jsonify({'error': 'Email không tồn tại'}), 404

        # Trong môi trường thực tế, bạn sẽ kiểm tra mật khẩu qua Firebase Auth
        # Ở đây chúng ta giả định xác thực thành công
        user_data = user_docs[0].to_dict()
        user_id = user_docs[0].id

        # Thiết lập phiên đăng nhập
        session['uid'] = user_id
        session['username'] = user_data.get('username')

        return jsonify({'success': True, 'uid': user_id, 'username': user_data.get('username')}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200


@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        # Lấy tất cả bài đăng từ Firestore, sắp xếp theo thời gian tạo (mới nhất trước)
        posts_ref = db.collection('posts').order_by('created_at', direction=firestore.Query.DESCENDING)
        posts = []

        for doc in posts_ref.stream():
            post_data = doc.to_dict()
            post_data['id'] = doc.id
            posts.append(post_data)

        return jsonify(posts), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    data = request.json
    try:
        # Tạo bài đăng mới trong Firestore
        post_data = {
            'title': data['title'],
            'price': data['price'],
            'description': data['description'],
            'image': data['image'],  # Trong thực tế, bạn cần xử lý upload ảnh
            'seller': session['username'],
            'seller_id': session['uid'],
            'contact': data['contact'],
            'created_at': firestore.SERVER_TIMESTAMP,
            'status': 'available'  # available, sold, cancelled
        }

        # Thêm vào Firestore
        post_ref = db.collection('posts').add(post_data)

        # Cập nhật danh sách bài đăng của người dùng
        user_ref = db.collection('users').document(session['uid'])
        user_ref.update({
            'sales': firestore.ArrayUnion([post_ref.id])
        })

        return jsonify({'success': True, 'post_id': post_ref.id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post_ref = db.collection('posts').document(post_id)
        post = post_ref.get()

        if not post.exists:
            return jsonify({'error': 'Bài đăng không tồn tại'}), 404

        post_data = post.to_dict()
        post_data['id'] = post.id

        return jsonify(post_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payment', methods=['POST'])
@login_required
def process_payment():
    data = request.json
    try:
        # Lấy thông tin bài đăng
        post_ref = db.collection('posts').document(data['post_id'])
        post = post_ref.get()

        if not post.exists:
            return jsonify({'error': 'Bài đăng không tồn tại'}), 404

        post_data = post.to_dict()

        # Kiểm tra xem bài đăng có còn khả dụng không
        if post_data['status'] != 'available':
            return jsonify({'error': 'Bài đăng đã được bán hoặc hủy'}), 400

        # Tạo giao dịch mới
        transaction_data = {
            'post_id': data['post_id'],
            'buyer_id': session['uid'],
            'seller_id': post_data['seller_id'],
            'amount': post_data['price'],
            'payment_method': data['payment_method'],
            'status': 'completed',  # completed, processing, cancelled
            'created_at': firestore.SERVER_TIMESTAMP
        }

        # Thêm vào Firestore
        transaction_ref = db.collection('transactions').add(transaction_data)

        # Cập nhật trạng thái bài đăng
        post_ref.update({
            'status': 'sold'
        })

        # Cập nhật lịch sử mua hàng của người dùng
        user_ref = db.collection('users').document(session['uid'])
        user_ref.update({
            'purchases': firestore.ArrayUnion([transaction_ref.id])
        })

        return jsonify({
            'success': True,
            'transaction_id': transaction_ref.id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/users/<user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    # Chỉ cho phép người dùng xem thông tin của chính họ hoặc admin
    if session['uid'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()

        if not user.exists:
            return jsonify({'error': 'Người dùng không tồn tại'}), 404

        user_data = user.to_dict()

        # Lấy lịch sử mua hàng
        purchases = []
        for purchase_id in user_data.get('purchases', []):
            transaction = db.collection('transactions').document(purchase_id).get().to_dict()
            if transaction:
                post = db.collection('posts').document(transaction['post_id']).get().to_dict()
                if post:
                    purchases.append({
                        'id': purchase_id,
                        'title': post.get('title'),
                        'image': post.get('image'),
                        'seller': post.get('seller'),
                        'price': post.get('price'),
                        'date': transaction.get('created_at'),
                        'status': transaction.get('status')
                    })

        # Lấy lịch sử bán hàng
        sales = []
        for sale_id in user_data.get('sales', []):
            post = db.collection('posts').document(sale_id).get().to_dict()
            if post:
                sales.append({
                    'id': sale_id,
                    'title': post.get('title'),
                    'image': post.get('image'),
                    'price': post.get('price'),
                    'status': post.get('status'),
                    'date': post.get('created_at')
                })

        return jsonify({
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'phone': user_data.get('phone'),
            'address': user_data.get('address'),
            'created_at': user_data.get('created_at'),
            'purchases': purchases,
            'sales': sales
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    # Chỉ cho phép người dùng cập nhật thông tin của chính họ
    if session['uid'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    try:
        # Cập nhật thông tin người dùng trong Firestore
        user_ref = db.collection('users').document(user_id)

        # Cho phép cập nhật các trường cụ thể
        update_data = {}
        allowed_fields = ['username', 'phone', 'address']

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if update_data:
            user_ref.update(update_data)

        return jsonify({'success': True}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)