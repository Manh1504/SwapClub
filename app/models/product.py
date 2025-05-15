from app.services.firebase_service import get_firestore_db
from datetime import datetime
import uuid


class Product:
    def __init__(self, id=None, title=None, description=None, price=None,
                 condition=None, category=None, seller_id=None,
                 images=None, status="available", created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.price = price
        self.condition = condition  # mới, đã qua sử dụng, v.v.
        self.category = category
        self.seller_id = seller_id
        self.images = images or []  # danh sách các URL ảnh từ Cloudinary
        self.status = status  # available, sold, pending
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @staticmethod
    def get_by_id(product_id):
        """Lấy sản phẩm từ Firestore bằng ID"""
        if not product_id:
            return None

        db = get_firestore_db()
        product_doc = db.collection('products').document(product_id).get()

        if not product_doc.exists:
            return None

        product_data = product_doc.to_dict()
        return Product(
            id=product_id,
            title=product_data.get('title'),
            description=product_data.get('description'),
            price=product_data.get('price'),
            condition=product_data.get('condition'),
            category=product_data.get('category'),
            seller_id=product_data.get('seller_id'),
            images=product_data.get('images', []),
            status=product_data.get('status', 'available'),
            created_at=product_data.get('created_at'),
            updated_at=product_data.get('updated_at')
        )

    @staticmethod
    def get_all(limit=20, status=None, category=None, seller_id=None):
        """Lấy danh sách sản phẩm theo các tiêu chí"""
        db = get_firestore_db()
        query = db.collection('products')

        # Lọc theo trạng thái nếu có
        if status:
            query = query.where('status', '==', status)

        # Lọc theo danh mục nếu có
        if category:
            query = query.where('category', '==', category)

        # Lọc theo người bán nếu có
        if seller_id:
            query = query.where('seller_id', '==', seller_id)

        # Sắp xếp theo thời gian tạo mới nhất
        query = query.order_by('created_at', direction='DESCENDING').limit(limit)

        products = []
        for doc in query.stream():
            product_data = doc.to_dict()
            products.append(Product(
                id=doc.id,
                title=product_data.get('title'),
                description=product_data.get('description'),
                price=product_data.get('price'),
                condition=product_data.get('condition'),
                category=product_data.get('category'),
                seller_id=product_data.get('seller_id'),
                images=product_data.get('images', []),
                status=product_data.get('status', 'available'),
                created_at=product_data.get('created_at'),
                updated_at=product_data.get('updated_at')
            ))

        return products

    def save(self):
        """Lưu hoặc cập nhật sản phẩm vào Firestore"""
        try:
            db = get_firestore_db()
            self.updated_at = datetime.now()

            data = self.to_dict()

            # Lưu vào Firestore
            db.collection('products').document(self.id).set(data)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu sản phẩm: {e}")
            return False

    def update_status(self, status):
        """Cập nhật trạng thái sản phẩm"""
        try:
            self.status = status
            self.updated_at = datetime.now()

            db = get_firestore_db()
            db.collection('products').document(self.id).update({
                'status': status,
                'updated_at': self.updated_at
            })
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật trạng thái sản phẩm: {e}")
            return False

    def to_dict(self):
        """Chuyển đổi dữ liệu sản phẩm thành dictionary"""
        return {
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'condition': self.condition,
            'category': self.category,
            'seller_id': self.seller_id,
            'images': self.images,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }