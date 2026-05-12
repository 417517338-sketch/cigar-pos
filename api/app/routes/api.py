"""
API Routes — Internal API endpoints
"""
from flask import Blueprint, jsonify, request
from app import db
from app.models import Category, Product, Order, Discount, StockLog
from datetime import datetime, timedelta
from sqlalchemy import func

api_bp = Blueprint('api', __name__)


@api_bp.route('/categories')
def categories():
    categories_list = Category.query.filter_by(status='active').order_by(Category.sort_order).all()
    return jsonify([{
        'id': c.id, 'name_zh': c.name_zh, 'name_en': c.name_en,
        'name_ru': c.name_ru, 'sort_order': c.sort_order
    } for c in categories_list])


@api_bp.route('/products')
def products():
    category_id = request.args.get('category_id', type=int)
    query = Product.query.filter(Product.status == 'active', Product.deleted_at.is_(None))
    if category_id:
        query = query.filter_by(category_id=category_id)
    products_list = query.all()
    return jsonify([{
        'id': p.id, 'category_id': p.category_id,
        'name_zh': p.name_zh, 'name_en': p.name_en, 'name_ru': p.name_ru,
        'spec': p.spec, 'price': float(p.price),
        'stock': p.stock, 'stock_alert': p.stock_alert,
        'image_url': p.image_url,
        'is_low_stock': p.is_low_stock, 'is_out_of_stock': p.is_out_of_stock,
    } for p in products_list])


@api_bp.route('/sales/summary')
def sales_summary():
    """Sales summary for dashboard charts."""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    # Daily sales trend
    daily = db.session.query(
        func.date(Order.paid_at).label('date'),
        func.sum(Order.total).label('sales'),
        func.sum(Order.profit).label('profit'),
        func.count(Order.id).label('orders'),
    ).filter(
        Order.payment_status == 'paid',
        Order.paid_at >= start_date
    ).group_by(func.date(Order.paid_at)).order_by(func.date(Order.paid_at)).all()
    # Category breakdown
    category_sales = db.session.query(
        Category.name_zh,
        func.sum(Order.total).label('total'),
    ).join(Order.items).filter(
        Order.payment_status == 'paid',
        Order.paid_at >= start_date
    ).group_by(Category.id).all()
    return jsonify({
        'daily': [{'date': str(r.date), 'sales': float(r.sales or 0),
                   'profit': float(r.profit or 0), 'orders': r.orders} for r in daily],
        'categories': [{'name': r.name_zh, 'total': float(r.total or 0)} for r in category_sales],
    })
