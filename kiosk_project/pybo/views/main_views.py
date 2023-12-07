from flask import Blueprint
from flask import render_template, request, redirect, url_for
from datetime import datetime
from pybo import db
from pybo.models import MenuItem, Order

bp = Blueprint('main', __name__, url_prefix='/')

# 메뉴와 재고 초기화


# 주문 목록 초기화
orders = []

# 주문 번호 초기화
order_number = 1


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/main')
def main():
    menu_items = MenuItem.query.all()
    menu = {item.name: {'price': item.price, 'stock': item.stock} for item in menu_items}

    return render_template('menu.html', menu=menu)

@bp.route('/takeout')
def takeout():
    menu_items = MenuItem.query.all()
    menu = {item.name: {'price': item.price, 'stock': item.stock} for item in menu_items}

    return render_template('menu.html', menu=menu)

if __name__ == '__main__':
    bp.run(debug=True)



@bp.route('/order', methods=['POST'])
def order():
    global order_number
    item = request.form.get('item')
    quantity = int(request.form.get('quantity'))


    menu_item = MenuItem.query.filter_by(name=item).first()

    if not menu_item:
        return "주문 항목을 찾을 수 없습니다."

    if menu_item.stock >= quantity:
        menu_item.stock -= quantity
        order = Order(
            order_number=order_number,
            status='준비 중',
            item=item,
            quantity=quantity,
            temperature=request.form.get('temperature_' + item),
            timestamp=datetime.now()
        )
        db.session.add(order)
        db.session.commit()
        order_number += 1
        
        # 합계 금액 계산
        orders = Order.query.filter_by(status='준비 중').all()

        total_price = sum(menu_item.price * order.quantity for order in orders)

        menu_items = MenuItem.query.all()
        menu = {item.name: {'price': item.price, 'stock': item.stock} for item in menu_items}

        return render_template('menu.html', menu=menu, orders=orders, total_price=total_price)
    else:
        return "재고가 부족합니다."

@bp.route('/orderlist')
def view_order_list():
    orders = Order.query.all()
    return render_template('order_list.html', orders=orders)

@bp.route('/orderlist_')
def view_order_list_():
    orders = Order.query.all()
    return render_template('order_list_.html', orders=orders)

@bp.route('/complete/<int:order_number>', methods=['POST'])
def complete_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    if order:
        order.status = '완료'
        db.session.commit()
    return redirect(url_for('main.view_order_list'))

@bp.route('/cancel/<int:order_number>', methods=['POST'])
def cancel_order(order_number):
    order = Order.query.filter_by(order_number=order_number, status='준비 중').first()
    if order:
        # 주문 취소한 메뉴 아이템을 식별하고 해당 아이템의 재고를 증가시킴
        menu_item = MenuItem.query.filter_by(name=order.item).first()
        if menu_item:
            menu_item.stock += order.quantity  # 재고 증가
            db.session.delete(order)  # 주문 삭제
            db.session.commit()

    return redirect(url_for('main.view_order_list'))
    # if order:
    #     db.session.delete(order)
    #     db.session.commit()

    return redirect(url_for('main.view_order_list'))

@bp.route('/cart')
def show_cart():
    menu_items = MenuItem.query.all()
    orders = Order.query.filter_by(status='준비 중').all()
    total_price = sum(menu_item.price * order.quantity for order in orders for menu_item in menu_items if menu_item.name == order.item)
    return render_template('cart.html', orders=orders, total_price=total_price)
   
@bp.route('/clear_cart', methods=['POST'])
# def clear_cart():
#     Order.query.filter_by(status='준비 중').delete()
#     db.session.commit()
#     return redirect(url_for('main.index'))
def clear_cart():
    orders = Order.query.filter_by(status='준비 중').all()
    
    # 주문을 취소하면 재고를 다시 쌓습니다.
    for order in orders:
        menu_item = MenuItem.query.filter_by(name=order.item).first()
        if menu_item:
            menu_item.stock += order.quantity

    # 주문 목록을 삭제합니다.
    Order.query.filter_by(status='준비 중').delete()
    db.session.commit()
    
    return redirect(url_for('main.index'))