from models import db, User
from flask_jwt_extended import create_access_token
import re


class UserService:
    @staticmethod
    def create_user(username, email, password, is_admin=False):
        """Create a new user"""
        # Validate inputs
        if not username or not email or not password:
            return None, "Username, email and password are required"

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return None, "Invalid email format"

        # Validate password strength (basic validation)
        if len(password) < 6:
            return None, "Password must be at least 6 characters long"

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return None, "Username already exists"

        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return None, "Email already exists"

        # Create new user
        user = User(
            username=username,
            email=email,
            password=password,  # In production, should hash password
            is_admin=is_admin
        )

        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def authenticate(username, password):
        """Authenticate a user and return a token"""
        # Kiểm tra xem đầu vào có phải là email không
        if '@' in username:
            user = User.query.filter_by(email=username).first()
        else:
            user = User.query.filter_by(username=username).first()

        if not user or user.password != password:  # Should use password hashing
            return None, "Invalid username or password"

        # Create access token
        access_token = create_access_token(identity=user.id)
        return {"user": user.to_dict(), "token": access_token}, None

    @staticmethod
    def get_user_by_id(user_id):
        """Get a user by ID"""
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        return user, None

    @staticmethod
    def get_all_users():
        """Get all users (admin function)"""
        users = User.query.all()
        return [user.to_dict() for user in users]

    @staticmethod
    def delete_user(user_id):
        """Delete a user (admin function)"""
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        try:
            db.session.delete(user)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_user(user_id, data):
        """Update user information"""
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"

        try:
            # Cập nhật các trường được cung cấp
            if 'username' in data:
                # Kiểm tra xem username mới đã tồn tại chưa (nếu khác username hiện tại)
                if data['username'] != user.username:
                    existing_user = User.query.filter_by(username=data['username']).first()
                    if existing_user:
                        return None, "Username already exists"
                user.username = data['username']

            if 'email' in data:
                # Kiểm tra xem email mới đã tồn tại chưa (nếu khác email hiện tại)
                if data['email'] != user.email:
                    existing_email = User.query.filter_by(email=data['email']).first()
                    if existing_email:
                        return None, "Email already exists"

                # Validate email format
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, data['email']):
                    return None, "Invalid email format"

                user.email = data['email']

            if 'password' in data:
                # Validate password strength
                if len(data['password']) < 6:
                    return None, "Password must be at least 6 characters long"
                user.password = data['password']  # Should hash password

            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)