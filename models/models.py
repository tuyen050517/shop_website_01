# models/models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric, Float, Integer, String, Text

# KHỞI TẠO DB ĐÚNG CÁCH — KHÔNG IMPORT LẠI models.py
db = SQLAlchemy()


# BẢNG USER

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    gmail = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))



# BẢNG OTP

class OtpRegister(db.Model):
    __tablename__ = "otp_register"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    otp_code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expire_at = db.Column(db.DateTime, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)


# BẢNG PRODUCT

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(Numeric(15, 0))
    image_url = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    brand = db.Column(db.String(100))
    chipset = db.Column(db.String(100))
    ram = db.Column(db.String(50))
    storage = db.Column(db.String(50))
    battery = db.Column(db.Integer)
    screen_size = db.Column(db.Float)
    weight = db.Column(db.Float)
    performance_score = db.Column(db.Float)
    release_year = db.Column(db.Integer)



# BẢNG GIỎ HÀNG

class CartItem(db.Model):
    __tablename__ = "cart_item"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(Numeric(15, 0), nullable=False, default=0)

    user = db.relationship("User", backref="cart_items", lazy=True)
    product = db.relationship("Product", backref="cart_items", lazy="joined")

    def __init__(self, user_id, product_id, quantity=1):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

        product = Product.query.get(product_id)
        self.total_price = (product.price * quantity) if product else 0

    def update_total(self):
        if self.product:
            self.total_price = self.product.price * self.quantity



# BẢNG ORDER

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(Numeric(15, 0), nullable=False)
    payment_method = db.Column(db.String(50), default="Bank")
    status = db.Column(db.String(50), default="Chờ thanh toán")
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    bank_account_name = db.Column(db.String(100))
    transfer_note = db.Column(db.String(255))
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship("User", backref="orders", lazy=True)



# BẢNG ADMIN

class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    fullnamead = db.Column(db.String(100))
    gmail = db.Column(db.String(100))
    usernamead = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
