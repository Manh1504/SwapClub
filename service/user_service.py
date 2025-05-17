from models import db, User
from flask_jwt_extended import create_access_token


class UserService:
    @staticmethod
    def create_user(username, email, password, is_admin=False):
        """Create a new user"""
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
            password=password,
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
        user = User.query.filter_by(username=username).first()

        if not user or user.password != password:
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