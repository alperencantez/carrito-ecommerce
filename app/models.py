from sqlalchemy import Boolean
from flask_login import UserMixin
from app.config import login, db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_seller = db.Column(Boolean, default=False)
    order_id = db.relationship("Order", backref="user", uselist=False)

    def __repr__(self):
        return f"{self.password} {self.email} {self.is_seller}"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(300), nullable=False)
    desc = db.Column(db.String(300), nullable=True)
    seller = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"{self.name} {self.price} {self.image} {self.desc} {self.seller}"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_done = db.Column(Boolean, default=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    customer_phone = db.Column(db.String(20))
    customer_name = db.Column(db.String(100))
    customer_last_name = db.Column(db.String(100))
    customer_email = db.Column(db.String(100))
    customer_notes = db.Column(db.String(100))
    address = db.Column(db.String(1000))
    product_name = db.Column(db.String(200), nullable=False)
    product_unit_price = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer)
    seller_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    def __repr__(self):
        return f"{self.id} {self.customer_id} {self.customer_phone} {self.customer_name} {self.customer_last_name} {self.customer_notes} {self.customer_email} {self.address} {self.product_id} {self.quantity}"


class PendingOrders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    customer_email = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    product_quantity = db.Column(db.String(250), nullable=False)

    def __repr__(self) -> str:
        return f"{self.id} {self.date} {self.customer_email} {self.customer_id} {self.seller_id} {self.product_quantity} {self.total} {self.address}"
