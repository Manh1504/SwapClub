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
            # Validate numeric inputs
            quantity = int(quantity)
            price = float(price)

            if quantity <= 0:
                return None, "Quantity must be greater than 0"

            if price <= 0:
                return None, "Price must be greater than 0"
        except (ValueError, TypeError):
            return None, "Quantity must be an integer and price must be a number"

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
                contact_info=contact_info,
                is_active=True  # Add an active flag
            )

            db.session.add(post)
            db.session.commit()
            return post, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_all_posts():
        """Get all active posts"""
        # Chỉ lấy các bài đăng còn active (số lượng > 0)
        posts = Post.query.filter_by(is_active=True).order_by(Post.created_at.desc()).all()
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
        posts = Post.query.filter(
            Post.product_type.like(f"%{product_name}%"),
            Post.is_active == True
        ).order_by(Post.created_at.desc()).all()
        return [post.to_dict() for post in posts]

    @staticmethod
    def search_posts_by_price_range(min_price, max_price):
        """Search posts by price range"""
        query = Post.query.filter_by(is_active=True)

        if min_price is not None:
            query = query.filter(Post.price >= min_price)
        if max_price is not None:
            query = query.filter(Post.price <= max_price)

        posts = query.order_by(Post.created_at.desc()).all()
        return [post.to_dict() for post in posts]

    @staticmethod
    def delete_post(post_id):
        """Delete a post"""
        post = Post.query.get(post_id)
        if not post:
            return False, "Post not found"

        try:
            db.session.delete(post)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_post(post_id, user_id, data):
        """Update a post"""
        post, error = PostService.get_post_by_id(post_id)
        if error:
            return None, error

        # Kiểm tra xem người dùng có quyền sửa bài đăng không
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"

        if not user.is_admin and post.user_id != user_id:
            return None, "Unauthorized to update this post"

        try:
            # Cập nhật các trường được cung cấp
            if 'product_type' in data:
                post.product_type = data['product_type']

            if 'description' in data:
                post.description = data['description']

            if 'contact_info' in data:
                post.contact_info = data['contact_info']

            if 'quantity' in data:
                try:
                    quantity = int(data['quantity'])
                    if quantity <= 0:
                        return None, "Quantity must be greater than 0"
                    post.quantity = quantity
                    post.is_active = quantity > 0
                except (ValueError, TypeError):
                    return None, "Quantity must be an integer"

            if 'price' in data:
                try:
                    price = float(data['price'])
                    if price <= 0:
                        return None, "Price must be greater than 0"
                    post.price = price
                except (ValueError, TypeError):
                    return None, "Price must be a number"

            db.session.commit()
            return post, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)