"""
StockLog Model
"""
from datetime import datetime
from app import db


class StockLog(db.Model):
    __tablename__ = 'stock_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    type = db.Column(db.Enum('in', 'out', 'adjust'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(256), nullable=True)
    operator = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', back_populates='stock_logs')
