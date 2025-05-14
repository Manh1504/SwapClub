from flask import Flask, request, jsonify, render_template
from firebase_admin import credentials, initialize_app, db, auth
from services.cloudinary_service import upload_image
import os

app = Flask(__name__)
cred = credentials.Certificate("swap.json")

initialize_app(cred, {
    'databaseURL': 'https://swap-ba42e-default-rtdb.firebaseio.com/'
})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['POST'])
def add_product():
    # Xác thực Firebase ID token
    id_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    try:
        decoded = auth.verify_id_token(id_token)
        user_email = decoded['email']
    except:
        return jsonify({'error': 'Invalid token'}), 401

    # Lấy dữ liệu từ form
    name = request.form.get('name')
    description = request.form.get('description')
    image_file = request.files.get('image')

    if not all([name, image_file]):
        return jsonify({'error': 'Missing fields'}), 400

    # Upload ảnh lên Cloudinary
    image_url = upload_image(image_file)

    # Lưu dữ liệu vào Firebase Realtime DB
    ref = db.reference('products')
    new_product = {
        'name': name,
        'description': description,
        'image_url': image_url,
        'user': user_email
    }
    ref.push(new_product)
    return jsonify({'message': 'Product added successfully'})

@app.route('/api/products', methods=['GET'])
def get_products():
    ref = db.reference('products')
    return jsonify(ref.get() or {})

if __name__ == '__main__':
    app.run(debug=True)
