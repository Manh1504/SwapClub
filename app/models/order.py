from app.services.firebase_service import get_firestore_db
from datetime import datetime
import uuid


class Order:
    def __init__(self, id=None, product_id=None, buyer_id=None, seller_id=None,
                 price=None, status="pending", shipping_address=None,
                 payment_method=None, payment_status=None,
                 created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.product_id = product_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.price = price
        self.status = status  # pending, confirmed, shipped, delivered, cancelled
        self.shipping_address = shipping_address
        self.payment_method = payment_method
        self.payment_status = payment_status  # pending, paid, failed
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @staticmethod
    def get_by_id(order_id):
        """Lấy đơn hàng từ Firestore bằng ID"""
        if not order_id:
            return None

        db = get_firestore_db()
        order_doc = db.collection('orders').document(order_id).get()

        if not order_doc.exists:
            return None

        order_data = order_doc.to_dict()
        return Order(
            id=order_id,
            product_id=order_data.get('product_id'),
            buyer_id=order_data.get('buyer_id'),
            seller_id=order_data.get('seller_id'),
            price=order_data.get('price'),
            status=order_data.get('status'),
            shipping_address=order_data.get('shipping_address'),
            payment_method=order_data.get('payment_method'),
            payment_status=order_data.get('payment_status'),
            created_at=order_data.get('created_at'),
            updated_at=order_data.get('updated_at')
        )

    @staticmethod
    def get_by_buyer(buyer_id, limit=20):
        """Lấy danh sách đơn hàng của người mua"""
        db = get_firestore_db()
        query = db.collection('orders').where('buyer_id', '==', buyer_id)
        query = query.order_by('created_at', direction='DESCENDING').limit(limit)

        orders = []
        for doc in query.stream():
            order_data = doc.to_dict()
            orders.append(Order(
                id=doc.id,
                product_id=order_data.get('product_id'),
                buyer_id=order_data.get('buyer_id'),
                seller_id=order_data.get('seller_id'),
                price=order_data.get('price'),
                status=order_data.get('status'),
                shipping_address=order_data.get('shipping_address'),
                payment_method=order_data.get('payment_method'),
                payment_status=order_data.get('payment_status'),
                created_at=order_data.get('created_at'),
                updated_at=order_data.get('updated_at')
            ))

        return orders

    @staticmethod
    def get_by_seller(seller_id, limit=20):
        """Lấy danh sách đơn hàng của người bán"""
        db = get_firestore_db()
        query = db.collection('orders').where('seller_id', '==', seller_id)
        query = query.order_by('created_at', direction='DESCENDING').limit(limit)

        orders = []
        for doc in query.stream():
            order_data = doc.to_dict()
            orders.append(Order(
                id=doc.id,
                product_id=order_data.get('product_id'),
                buyer_id=order_data.get('buyer_id'),
                seller_id=order_data.get('seller_id'),
                price=order_data.get('price'),
                status=order_data.get('status'),
                shipping_address=order_data.get('shipping_address'),
                payment_method=order_data.get('payment_method'),
                payment_status=order_data.get('payment_status'),
                created_at=order_data.get('created_at'),
                updated_at=order_data.get('updated_at')
            ))

        return orders

    def save(self):
        """Lưu đơn hàng vào Firestore"""
        try:
            db = get_firestore_db()
            self.updated_at = datetime.now()

            data = self.to_dict()

            db.collection('orders').document(self.id).set(data)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu đơn hàng: {e}")
            return False

    def update_status(self, status):
        """Cập nhật trạng thái đơn hàng"""
        try:
            self.status = status
            self.updated_at = datetime.now()

            db = get_firestore_db()
            db.collection('orders').document(self.id).update({
                'status': status,
                'updated_at': self.updated_at
            })
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật trạng thái đơn hàng: {e}")
            return False

    def update_payment_status(self, payment_status):
        """Cập nhật trạng thái thanh toán"""
        try:
            self.payment_status = payment_status
            self.updated_at = datetime.now()

            db = get_firestore_db()
            db.collection('orders').document(self.id).update({
                'payment_status': payment_status,
                'updated_at': self.updated_at
            })
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật trạng thái thanh toán: {e}")
            return False

    def to_dict(self):
        """Chuyển đổi dữ liệu đơn hàng thành dictionary"""
        return {
            'product_id': self.product_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'price': self.price,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }