from models import db, Order, Post, User


class OrderService:
    @staticmethod
    def create_order(post_id, buyer_id, quantity):
        """Create a new order"""
        try:
            # Get the post
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"

            # Check if buyer exists
            buyer = User.query.get(buyer_id)
            if not buyer:
                return None, "Buyer not found"

            # Check if buyer is not the seller
            if post.user_id == buyer_id:
                return None, "You cannot purchase your own product"

            # Check if quantity is available
            if quantity > post.quantity:
                return None, "Not enough quantity available"

            # Create order
            order = Order(
                post_id=post_id,
                seller_id=post.user_id,
                buyer_id=buyer_id,
                quantity=quantity,
                price=post.price
            )

            # Update post quantity
            post.quantity -= quantity

            # If quantity becomes zero, mark post as inactive or delete it
            if post.quantity == 0:
                post.is_active = False

            db.session.add(order)
            db.session.commit()
            return order, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_orders_by_buyer(buyer_id):
        """Get all orders by a specific buyer"""
        orders = Order.query.filter_by(buyer_id=buyer_id).order_by(Order.created_at.desc()).all()
        return [order.to_dict() for order in orders]

    @staticmethod
    def get_orders_by_seller(seller_id):
        """Get all orders for a specific seller"""
        orders = Order.query.filter_by(seller_id=seller_id).order_by(Order.created_at.desc()).all()
        return [order.to_dict() for order in orders]

    @staticmethod
    def get_all_orders():
        """Get all orders (admin function)"""
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return [order.to_dict() for order in orders]

    @staticmethod
    def get_order_by_id(order_id):
        """Get order by ID"""
        order = Order.query.get(order_id)
        if not order:
            return None
        return order.to_dict()