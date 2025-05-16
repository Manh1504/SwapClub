from models import db, Post, User
from sqlalchemy import or_


class PostService:
    @staticmethod
    def create_post(user_id, product_type, quantity, price, description, contact_info):
        """Create a new post"""
        # Validate input
        if not all([product_type, quantity, price, contact_info]):
            return None, "Missing required fields"

        try:
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"

            post = Post(
                user_id=user_id,
                product_type=product_type,
                quantity=quantity,
                price=price,
                description=description,
                contact_info=contact_info
            )

            db.session.add(post)
            db.session.commit()
            return post, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_all_posts():
        """Get all posts"""
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return [post.to_dict() for post in posts]

    @staticmethod
    def get_posts_by_user(user_id):
        """Get all posts by a specific user"""
        posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
        return [post.to_dict() for post in posts]

    @staticmethod
    def get_post_by_id(post_id):
        """Get a post by ID"""
        post = Post.query.get(post_id)
        if not post:
            return None, "Post not found"
        return post, None

    @staticmethod
    def search_posts_by_product_name(product_name):
        """Search posts by product name"""
        posts = Post.query.filter(Post.product_type.like(f"%{product_name}%")).order_by(Post.created_at.desc()).all()
        return [post.to_dict() for post in posts]

    @staticmethod
    def search_posts_by_price_range(min_price, max_price):
        """Search posts by price range"""
        query = Post.query

        if min_price is not None:
            query = query.filter(Post.price >= min_price)
        if max_price is not None:
            query = query.filter(Post.price <= max_price)

        posts = query.order_by(Post.created_at.desc()).all()
        return [post.to_dict() for post in posts]
