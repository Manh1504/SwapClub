from models import db, User
from flask_jwt_extended import create_access_token


class UserService:
    @staticmethod
    def create_user(username, password):
        """Create a new user"""
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return None, "Username already exists"

        # Create new user
        user = User(username=username)
        user.set_password(password)

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

        if not user or not user.check_password(password):
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