from app import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name_zh = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), default='')
    name_ru = db.Column(db.String(100), default='')
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    products = db.relationship('Product', back_populates='category', lazy='dynamic')

    def get_name(self, lang='zh'):
        return getattr(self, f'name_{lang}', self.name_zh)

    def to_dict(self):
        return {
            "id": self.id,
            "name_zh": self.name_zh,
            "name_en": self.name_en,
            "name_ru": self.name_ru,
            "sort_order": self.sort_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }