"""
Admin Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import Category, Product, Order, Discount, StockLog, Setting, User
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    # Key metrics
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    today_sales = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(
        Order.payment_status == 'paid',
        func.date(Order.paid_at) == today
    ).scalar()

    today_orders = Order.query.filter(
        Order.payment_status == 'paid',
        func.date(Order.paid_at) == today
    ).count()

    month_sales = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(
        Order.payment_status == 'paid',
        func.date(Order.paid_at) >= month_start
    ).scalar()

    month_orders = Order.query.filter(
        Order.payment_status == 'paid',
        func.date(Order.paid_at) >= month_start
    ).count()

    month_profit = db.session.query(func.coalesce(func.sum(Order.profit), 0)).filter(
        Order.payment_status == 'paid',
        func.date(Order.paid_at) >= month_start
    ).scalar()

    # Net profit = gross profit - operational cost (from settings)
    operational_cost = float(Setting.get('operational_cost', 0) or 0)
    net_profit = float(month_profit) - operational_cost

    # Low stock products
    low_stock_products = Product.query.filter(
        Product.stock <= Product.stock_alert,
        Product.status == 'active',
        Product.deleted_at.is_(None)
    ).order_by(Product.stock).limit(10).all()

    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
        today_sales=today_sales,
        today_orders=today_orders,
        month_sales=month_sales,
        month_orders=month_orders,
        month_profit=month_profit,
        net_profit=net_profit,
        low_stock_products=low_stock_products,
        recent_orders=recent_orders,
    )


@admin_bp.route('/categories')
@login_required
def categories():
    categories_list = [c.to_dict() for c in Category.query.order_by(Category.sort_order).all()]
    return render_template('admin/categories.html', categories=categories_list)


@admin_bp.route('/categories/save', methods=['POST'])
@login_required
def save_category():
    data = request.get_json()
    category_id = data.get('id')
    if category_id:
        cat = Category.query.get(category_id)
        if not cat:
            return jsonify({'success': False, 'error': 'Not found'}), 404
    else:
        cat = Category()
        db.session.add(cat)
    cat.name_zh = data['name_zh']
    cat.name_en = data['name_en']
    cat.name_ru = data['name_ru']
    cat.sort_order = int(data.get('sort_order', 0))
    cat.status = data.get('status', 'active')
    db.session.commit()
    return jsonify({'success': True, 'id': cat.id})


@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    cat = Category.query.get(id)
    if not cat:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    # Check if has products
    if cat.products.filter_by(deleted_at=None).count() > 0:
        return jsonify({'success': False, 'error': 'Cannot delete category with products'}), 400
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/products')
@login_required
def products():
    categories = Category.query.filter_by(status='active').all()
    products_list = [p.to_dict() for p in Product.query.filter(
        Product.deleted_at.is_(None)
    ).order_by(Product.created_at.desc()).all()]
    categories = [c.to_dict() for c in Category.query.filter_by(status='active').all()]
    return render_template('admin/products.html', products=products_list, categories=categories)


@admin_bp.route('/products/save', methods=['POST'])
@login_required
def save_product():
    data = request.get_json()
    product_id = data.get('id')
    if product_id:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Not found'}), 404
    else:
        product = Product()
        db.session.add(product)
    product.category_id = int(data['category_id'])
    product.name_zh = data['name_zh']
    product.name_en = data['name_en']
    product.name_ru = data['name_ru']
    product.spec = data.get('spec', '')
    product.price = float(data['price'])
    product.cost_price = float(data.get('cost_price', 0))
    product.stock = int(data.get('stock', 0))
    product.stock_alert = int(data.get('stock_alert', 3))
    product.image_url = data.get('image_url', '')
    product.status = data.get('status', 'active')
    db.session.commit()
    return jsonify({'success': True, 'id': product.id})


@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    product.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/stock')
@login_required
def stock():
    products_list = Product.query.filter(
        Product.deleted_at.is_(None)
    ).order_by(Product.stock).all()
    return render_template('admin/stock.html', products=products_list)


@admin_bp.route('/stock/adjust', methods=['POST'])
@login_required
def adjust_stock():
    data = request.get_json()
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    qty = int(data['quantity'])
    log_type = data['type']  # 'in' or 'out' or 'adjust'
    note = data.get('note', '')
    operator = current_user.username
    if log_type == 'in':
        product.stock += qty
    elif log_type == 'out':
        if product.stock < qty:
            return jsonify({'success': False, 'error': 'Insufficient stock'}), 400
        product.stock -= qty
    else:  # adjust
        product.stock = qty
    log = StockLog(
        product_id=product.id,
        type=log_type,
        quantity=qty if log_type != 'adjust' else (qty - product.stock + qty),
        balance=product.stock,
        note=note,
        operator=operator,
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'success': True, 'balance': product.stock})


@admin_bp.route('/sales')
@login_required
def sales():
    # Date range filter
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    orders = [o.to_dict() for o in Order.query.filter(
        Order.payment_status == 'paid',
        Order.paid_at >= start_date
    ).order_by(Order.paid_at.desc()).all()]
    return render_template('admin/sales.html', orders=orders, days=days)


@admin_bp.route('/discounts')
@login_required
def discounts():
    discounts_list = [d.to_dict() for d in Discount.query.order_by(Discount.created_at.desc()).all()]
    return render_template('admin/discounts.html', discounts=discounts_list)


@admin_bp.route('/discounts/save', methods=['POST'])
@login_required
def save_discount():
    data = request.get_json()
    discount_id = data.get('id')
    if discount_id:
        discount = Discount.query.get(discount_id)
    else:
        discount = Discount()
        db.session.add(discount)
    discount.code = data['code'].upper()
    discount.type = data['type']
    discount.value = float(data['value'])
    discount.min_amount = float(data.get('min_amount', 0))
    discount.valid_from = datetime.fromisoformat(data['valid_from']) if data.get('valid_from') else datetime.utcnow()
    discount.valid_until = datetime.fromisoformat(data['valid_until']) if data.get('valid_until') else None
    discount.status = data.get('status', 'active')
    db.session.commit()
    return jsonify({'success': True, 'id': discount.id})


@admin_bp.route('/discounts/delete/<int:id>', methods=['POST'])
@login_required
def delete_discount(id):
    discount = Discount.query.get(id)
    if not discount:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    db.session.delete(discount)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        data = request.form
        Setting.set('shop_name', data.get('shop_name', ''))
        Setting.set('operational_cost', data.get('operational_cost', 0))
        Setting.set('default_lang', data.get('default_lang', 'zh'))
        flash('Settings saved', 'success')
    shop_name = Setting.get('shop_name', 'Cigar Lounge')
    order_prefix = Setting.get('order_prefix', 'CL')
    currency_symbol = Setting.get('currency_symbol', '¥')
    operational_cost = Setting.get('operational_cost', 0)
    default_lang = Setting.get('default_lang', 'zh')
    low_stock_threshold = Setting.get('low_stock_threshold', 3)
    discounts = Discount.query.order_by(Discount.created_at.desc()).all()
    return render_template('admin/settings.html',
        shop_name=shop_name,
        order_prefix=order_prefix,
        currency_symbol=currency_symbol,
        operational_cost=operational_cost,
        default_lang=default_lang,
        low_stock_threshold=low_stock_threshold,
        discounts=[d.to_dict() for d in discounts],
    )


@admin_bp.route('/settings/save', methods=['POST'])
def settings_save():
    data = request.get_json() or {}
    Setting.set('shop_name', data.get('shop_name', 'Cigar Lounge'))
    Setting.set('order_prefix', data.get('order_prefix', 'CL'))
    Setting.set('currency_symbol', data.get('currency_symbol', '¥'))
    Setting.set('default_lang', data.get('default_lang', 'zh'))
    Setting.set('operational_cost', str(data.get('operational_cost', 0)))
    Setting.set('low_stock_threshold', str(data.get('low_stock_threshold', 3)))
    return jsonify(success=True)
