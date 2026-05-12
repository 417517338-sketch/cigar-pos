from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    discount_code = db.Column(db.String(30), nullable=True)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    cost_total = db.Column(db.Numeric(10, 2), default=0)
    profit = db.Column(db.Numeric(10, 2), default=0)
    payment_method = db.Column(db.String(20), nullable=True)
    payment_status = db.Column(db.String(20), default='pending')
    payment_qr = db.Column(db.String(500), nullable=True)
    ordered_at = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "subtotal": float(self.subtotal) if self.subtotal else 0,
            "discount_code": self.discount_code,
            "discount_amount": float(self.discount_amount) if self.discount_amount else 0,
            "total": float(self.total) if self.total else 0,
            "cost_total": float(self.cost_total) if self.cost_total else 0,
            "profit": float(self.profit) if self.profit else 0,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "ordered_at": self.ordered_at.isoformat() if self.ordered_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2), default=0)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": float(self.price) if self.price else 0,
            "cost_price": float(self.cost_price) if self.cost_price else 0,
            "quantity": self.quantity,
            "subtotal": float(self.subtotal) if self.subtotal else 0,
        }
