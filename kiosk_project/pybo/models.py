from pybo import db
from datetime import datetime

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Integer, nullable=False)
    item = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(128), nullable=False, default='준비 중')
    quantity = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)