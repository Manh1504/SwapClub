from flask_login import UserMixin
from app.services.firebase_service import get_firestore_db, get_firebase_auth
from datetime import datetime
import uuid


class User(UserMixin):
    def __init__(self, id=None, email=None, name=None, phone=None, address=None, created_at=None):
        self.id = id
        self.email = email
        self.name = name
        self.phone = phone
        self.address = address
        self.created_at = created_at or datetime.now()

    def get_id(self):
        return self.id

    @staticmethod
    def get_by_id(user_id):
        """Lấy thông tin người dùng từ Firestore bằng ID"""
        if not user_id:
            return None

        db = get_firestore_db()
        user_doc = db.collection('users').document(user_id).get()

        if not user_doc.exists:
            return None

        user_data = user_doc.to_dict()
        return User(
            id=user_id,
            email=user_data.get('email'),
            name=user_data.get('name'),
            phone=user_data.get('phone'),
            address=user_data.get('address'),
            created_at=user_data.get('created_at')
        )

    @staticmethod
    def get_by_email(email):
        """Lấy thông tin người dùng từ Firestore bằng email"""
        db = get_firestore_db()
        users = db.collection('users').where('email', '==', email).limit(1).stream()

        for user in users:
            user_data = user.to_dict()
            return User(
                id=user.id,
                email=user_data.get('email'),
                name=user_data.get('name'),
                phone=user_data.get('phone'),
                address=user_data.get('address'),
                created_at=user_data.get('created_at')
            )
        return None

    @staticmethod
    def create(email, password, name, phone=None, address=None):
        """Tạo tài khoản mới với Firebase Auth và lưu thông tin vào Firestore"""
        try:
            # Tạo người dùng trong Firebase Auth
            auth = get_firebase_auth()
            user_auth = auth.create_user_with_email_and_password(email, password)
            user_id = user_auth['localId']

            # Lưu thông tin chi tiết vào Firestore
            db = get_firestore_db()
            user_data = {
                'email': email,
                'name': name,
                'phone': phone,
                'address': address,
                'created_at': datetime.now()
            }

            db.collection('users').document(user_id).set(user_data)

            return User(
                id=user_id,
                email=email,
                name=name,
                phone=phone,
                address=address,
                created_at=datetime.now()
            )
        except Exception as e:
            print(f"Lỗi khi tạo người dùng: {e}")
            return None

    def update(self, name=None, phone=None, address=None):
        """Cập nhật thông tin người dùng"""
        try:
            db = get_firestore_db()
            data = {}

            if name is not None:
                data['name'] = name
                self.name = name

            if phone is not None:
                data['phone'] = phone
                self.phone = phone

            if address is not None:
                data['address'] = address
                self.address = address

            if data:
                db.collection('users').document(self.id).update(data)
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi cập nhật người dùng: {e}")
            return False

    def to_dict(self):
        """Chuyển đổi dữ liệu người dùng thành dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at
        }