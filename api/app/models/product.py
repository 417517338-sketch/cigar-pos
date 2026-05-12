from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name_zh = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), default='')
    name_ru = db.Column(db.String(200), default='')
    spec = db.Column(db.String(100), default='')
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2), default=0)
    stock = db.Column(db.Integer, default=0)
    stock_alert = db.Column(db.Integer, default=3)
    image_url = db.Column(db.String(500), default='')
    status = db.Column(db.String(20), default='active')
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = db.relationship('Category', back_populates='products')
    stock_logs = db.relationship('StockLog', back_populates='product', lazy='dynamic')

    @property
    def is_low_stock(self):
        return 0 < self.stock <= (self.stock_alert or 3)

    @property
    def is_out_of_stock(self):
        return self.stock <= 0

    def get_name(self, lang='zh'):
        return getattr(self, f'name_{lang}', self.name_zh)

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name_zh": self.name_zh,
            "name_en": self.name_en,
            "name_ru": self.name_ru,
            "spec": self.spec,
            "price": float(self.price) if self.price else 0,
            "cost_price": float(self.cost_price) if self.cost_price else 0,
            "stock": self.stock,
            "stock_alert": self.stock_alert,
            "image_url": self.image_url,
            "status": self.status,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }