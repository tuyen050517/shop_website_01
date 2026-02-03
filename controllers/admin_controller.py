from flask import session, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from models.models import db, Admin, User, Product, Order
from datetime import datetime
import os

class AdminController:

    # LOGIN

    @staticmethod
    def login(username, password):
        admin = Admin.query.filter_by(usernamead=username, password=password).first()
        if admin:
            session["admin_id"] = admin.id
            session["admin_name"] = admin.fullnamead
            return redirect(url_for("admin_bp.dashboard"))
        flash(" Sai tài khoản hoặc mật khẩu!", "error")
        return redirect(url_for("admin_bp.login"))

    @staticmethod
    def logout():
        session.pop("admin_id", None)
        session.pop("admin_name", None)
        return redirect(url_for("admin_bp.login"))

    # USERS
    @staticmethod
    def get_all_users():
        return User.query.all()

    #  PRODUCTS 

    @staticmethod
    def get_products_paginated(page=1, per_page=8):
        pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.page, pagination.pages

    @staticmethod
    def get_product_by_id(pid):
        return Product.query.get(pid)

    #  Handle add product 
    @staticmethod
    def handle_add_product(request):
        data = {key: request.form.get(key) for key in [
            "name", "price", "description", "category", "brand", "chipset", 
            "ram", "storage", "battery", "screen_size", "weight", 
            "performance_score", "release_year"
        ]}

        # Xử lý ảnh
        image_file = request.files.get("image_file")
        image_url = None
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            image_file.save(save_path)
            image_url = f"uploads/{filename}"

        # Gọi hàm thêm
        AdminController.add_product(image_url=image_url, **data)

    @staticmethod
    def handle_update_product(request, pid):
        data = {key: request.form.get(key) for key in [
            "name", "price", "description", "category", "brand", "chipset", 
            "ram", "storage", "battery", "screen_size", "weight", 
            "performance_score", "release_year"
        ]}
        image_file = request.files.get("image_file")
        image_url = request.form.get("current_image")

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            image_file.save(save_path)
            image_url = f"uploads/{filename}"

        AdminController.update_product(pid=pid, image_url=image_url, **data)

    @staticmethod
    def add_product(name, price, image_url, description, category, brand, chipset,
                    ram, storage, battery, screen_size, weight, performance_score, release_year):
        new_product = Product(
            name=name, price=float(price), image_url=image_url, description=description,
            category=category, brand=brand, chipset=chipset, ram=ram, storage=storage,
            battery=int(battery), screen_size=float(screen_size), weight=float(weight),
            performance_score=float(performance_score), release_year=int(release_year)
        )
        db.session.add(new_product)
        db.session.commit()

    @staticmethod
    def update_product(pid, name, price, image_url, description, category, brand, chipset,
                       ram, storage, battery, screen_size, weight, performance_score, release_year):
        product = Product.query.get(pid)
        if not product:
            return False
        product.name = name
        product.price = float(price)
        product.image_url = image_url
        product.description = description
        product.category = category
        product.brand = brand
        product.chipset = chipset
        product.ram = ram
        product.storage = storage
        product.battery = int(battery)
        product.screen_size = float(screen_size)
        product.weight = float(weight)
        product.performance_score = float(performance_score)
        product.release_year = int(release_year)
        db.session.commit()
        return True

    @staticmethod
    def delete_product(pid):
        product = Product.query.get(pid)
        if product:
            db.session.delete(product)
            db.session.commit()

    #  ORDERS 
    @staticmethod
    def get_all_orders():
        results = db.session.query(
            Order.id, User.fullname, Order.total_amount,
            Order.payment_method, Order.status, Order.bank_account
        ).join(User, User.id == Order.user_id).all()
        return results

    @staticmethod
    def confirm_payment(order_id):
        order = Order.query.get(order_id)
        if order and order.status == "Chờ thanh toán":
            order.status = "Đã thanh toán"
            order.paid_at = datetime.now()
            db.session.commit()
            return True
        return False
