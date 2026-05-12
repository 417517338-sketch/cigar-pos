"""
Front Routes — Customer-facing pages
"""
from flask import Blueprint, render_template, session, request, jsonify
from app import db
from app.models import Category, Product, Discount, Setting
from datetime import datetime

front_bp = Blueprint('front', __name__)

TRANSLATIONS = {
    'zh': {
        'cart': '购物车', 'checkout': '结算', 'pay': '支付', 'empty_cart': '购物车是空的',
        'total': '合计', 'discount': '折扣', 'payable': '应付', 'order_no': '订单号',
        'scan_to_pay': '扫码支付', 'payment_success': '支付成功', 'payment_failed': '支付失败',
        'low_stock': '仅剩', 'out_of_stock': '缺货', 'in_stock': '有货',
        'category_all': '全部',
        'hero_eyebrow': 'Premium Experience', 'hero_subtitle': '私人雪茄房 · 精选威士忌 · 尊贵体验',
        'menu_title': '精选菜单',
    },
    'en': {
        'cart': 'Cart', 'checkout': 'Checkout', 'pay': 'Pay', 'empty_cart': 'Cart is empty',
        'total': 'Total', 'discount': 'Discount', 'payable': 'Payable', 'order_no': 'Order No',
        'scan_to_pay': 'Scan to Pay', 'payment_success': 'Payment Success', 'payment_failed': 'Payment Failed',
        'low_stock': 'Only', 'out_of_stock': 'Out of Stock', 'in_stock': 'In Stock',
        'category_all': 'All',
        'hero_eyebrow': 'Premium Experience', 'hero_subtitle': 'Private Cigar Lounge · Curated Whiskies · Exclusive',
        'menu_title': 'Curated Menu',
    },
    'ru': {
        'cart': 'Корзина', 'checkout': 'Оплата', 'pay': 'Оплатить', 'empty_cart': 'Корзина пуста',
        'total': 'Итого', 'discount': 'Скидка', 'payable': 'К оплате', 'order_no': 'Заказ №',
        'scan_to_pay': 'Сканируйте для оплаты', 'payment_success': 'Оплата прошла', 'payment_failed': 'Оплата не прошла',
        'low_stock': 'Осталось', 'out_of_stock': 'Нет в наличии', 'in_stock': 'В наличии',
        'category_all': 'Все',
        'hero_eyebrow': 'Премиум опыт', 'hero_subtitle': 'Частная сигарная · Лучший виски · Эксклюзив',
        'menu_title': 'Избранное меню',
    },
}


def t(key, lang='zh'):
    return TRANSLATIONS.get(lang, TRANSLATIONS['zh']).get(key, key)


@front_bp.route('/')
def index():
    if 'lang' not in session:
        session['lang'] = Setting.get('default_lang', 'zh')
    lang = session['lang']
    categories = Category.query.order_by(Category.sort_order).all()
    products = Product.query.filter_by(status='active').all()
    cart = session.get('cart', {})
    cart_count = sum(item.get('qty', 0) for item in cart.values())
    shop_name = Setting.get('shop_name', 'Cigar Lounge')
    return render_template('front/index.html', categories=categories, products=products,
                           cart=cart, cart_count=cart_count, lang=lang, shop_name=shop_name)


@front_bp.route('/set-lang/<lang>')
def set_lang(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return '', 204


@front_bp.route('/cart/update', methods=['POST'])
def cart_update():
    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = data.get('quantity', 0)
    cart = session.get('cart', {})
    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = {'qty': quantity}
    session['cart'] = cart
    cart_count = sum(item.get('qty', 0) for item in cart.values())
    return jsonify({'cart_count': cart_count})


@front_bp.route('/checkout')
def checkout():
    if 'lang' not in session:
        session['lang'] = Setting.get('default_lang', 'zh')
    lang = session['lang']
    cart = session.get('cart', {})
    if not cart:
        shop_name = Setting.get('shop_name', 'Cigar Lounge')
        return render_template('front/index.html', categories=Category.query.order_by(Category.sort_order).all(),
                               products=Product.query.filter_by(status='active').all(),
                               cart={}, cart_count=0, lang=lang, shop_name=shop_name, t=lambda k: t(k, lang))
    product_ids = [int(k) for k in cart.keys()]
    products = {p.id: p for p in Product.query.filter(Product.id.in_(product_ids)).all()}
    subtotal = sum(cart[str(pid)]['qty'] * products[pid].price for pid in product_ids if pid in products)
    discount_code = session.get('discount_code')
    discount_amount = 0
    discount_rate = 0
    if discount_code:
        disc = Discount.query.filter_by(code=discount_code, is_active=True).first()
        if disc and disc.is_valid():
            discount_rate = disc.discount_rate
            discount_amount = subtotal * (1 - discount_rate)
    payable = subtotal - discount_amount
    shop_name = Setting.get('shop_name', 'Cigar Lounge')
    return render_template('front/checkout.html', cart=cart, products=products,
                           subtotal=subtotal, discount_amount=discount_amount,
                           discount_rate=discount_rate, payable=payable,
                           lang=lang, shop_name=shop_name, t=lambda k: t(k, lang))


@front_bp.route('/order/create', methods=['POST'])
def order_create():
    data = request.get_json()
    product_ids = list(data.get('cart', {}).keys())
    cart = session.get('cart', {})
    products = {p.id: p for p in Product.query.filter(Product.id.in_([int(k) for k in product_ids])).all()}
    subtotal = sum(cart[str(pid)]['qty'] * products[int(pid)].price for pid in product_ids if int(pid) in products)
    discount_code = session.get('discount_code')
    discount_amount = 0
    if discount_code:
        disc = Discount.query.filter_by(code=discount_code, is_active=True).first()
        if disc and disc.is_valid():
            discount_amount = subtotal * (1 - disc.discount_rate)
    from app.models import Order
    order = Order(subtotal=subtotal, discount_amount=discount_amount,
                  total=subtotal - discount_amount,
                  payment_method='pending')
    db.session.add(order)
    db.session.flush()
    from app.models import OrderItem
    for pid, item in cart.items():
        p = products.get(int(pid))
        if p:
            order_item = OrderItem(order_id=order.id, product_id=int(pid),
                                   quantity=item['qty'], unit_price=p.price,
                                   cost_price=p.cost_price or 0)
            db.session.add(order_item)
    db.session.commit()
    session.pop('cart', None)
    session.pop('discount_code', None)
    return jsonify({'order_id': order.id, 'payable': float(order.total)})


@front_bp.route('/order/<int:order_id>/pay', methods=['POST'])
def order_pay(order_id):
    from app.models import Order
    order = Order.query.get_or_404(order_id)
    if order.payment_status == 'paid':
        return jsonify({'error': 'Already paid'}), 400
    order.payment_status = 'paid'
    order.paid_at = datetime.utcnow()
    order.payment_method = 'qrcode'
    db.session.commit()
    return jsonify({'success': True})


@front_bp.route('/order/<int:order_id>/qrcode')
def order_qrcode(order_id):
    from app.models import Order
    order = Order.query.get_or_404(order_id)
    import qrcode
    import io
    import base64
    pay_url = f"https://cigar-lounge.local/order/{order.id}/pay"
    img = qrcode.make(pay_url)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return base64.b64encode(buf.getvalue()).decode(), 200, {'Content-Type': 'text/plain'}


@front_bp.route('/discount/apply', methods=['POST'])
def apply_discount():
    code = request.get_json().get('code', '').strip().upper()
    disc = Discount.query.filter_by(code=code, is_active=True).first()
    if disc and disc.is_valid():
        session['discount_code'] = code
        return jsonify({'success': True, 'discount_rate': disc.discount_rate})
    return jsonify({'error': 'Invalid code'}), 400
