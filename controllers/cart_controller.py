from flask import render_template, session, redirect, url_for, jsonify, flash
from models.models import db, CartItem, Product


class CartController:


    # HIỂN THỊ GIỎ HÀNG
    
    @staticmethod
    def show_cart():
        if "user_id" not in session:
            return redirect(url_for("auth_bp.auth"))

        user_id = session["user_id"]
        cart_items = CartItem.query.filter_by(user_id=user_id).all()

        total = 0
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product:
                item.product = product
                item.total_price = product.price * item.quantity
                total += item.total_price

        db.session.commit()
        print(f"Tổng cộng (Python): {total}")

        return render_template("cart.html", cart_items=cart_items, total=total)


    # THÊM SẢN PHẨM VÀO GIỎ HÀNG

    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        product = Product.query.get(product_id)
        if not product:
            flash("Sản phẩm không tồn tại!", "error")
            return redirect(url_for("home_bp.home"))

        existing_item = CartItem.query.filter_by(
            user_id=user_id, product_id=product_id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.total_price = existing_item.product.price * existing_item.quantity
        else:
            new_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                total_price=product.price * quantity
            )
            db.session.add(new_item)

        db.session.commit()
        flash("Đã thêm vào giỏ hàng!", "success")
        return redirect(url_for("cart_bp.cart"))

 
    # CẬP NHẬT SỐ LƯỢNG (TRUYỀN THỐNG - RELOAD)

    @staticmethod
    def update_quantity(product_id, action):
        if "user_id" not in session:
            return redirect(url_for("auth_bp.auth"))

        user_id = session["user_id"]
        item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if not item:
            flash("Không tìm thấy sản phẩm trong giỏ hàng!", "error")
            return redirect(url_for("cart_bp.cart"))

        if action == "increase":
            item.quantity += 1
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1

        item.total_price = item.product.price * item.quantity
        db.session.commit()
        flash("Đã cập nhật số lượng!", "success")

        return redirect(url_for("cart_bp.cart"))

    
    # XÓA SẢN PHẨM KHỎI GIỎ HÀNG
    
    @staticmethod
    def delete_item(product_id):
        if "user_id" not in session:
            return redirect(url_for("auth_bp.auth"))

        user_id = session["user_id"]
        item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if item:
            db.session.delete(item)
            db.session.commit()

        return redirect(url_for("cart_bp.cart"))

    # CẬP NHẬT SỐ LƯỢNG QUA AJAX (KHÔNG RELOAD)
    @staticmethod
    def update_quantity_ajax(product_id, action):
        if "user_id" not in session:
            return jsonify({"error": "not_logged_in"}), 401

        user_id = session["user_id"]
        item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if not item:
            return jsonify({"error": "not_found"}), 404

        if action == "increase":
            item.quantity += 1
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1

        item.total_price = item.product.price * item.quantity
        db.session.commit()

        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        total = sum(ci.product.price * ci.quantity for ci in cart_items)

        return jsonify({
            "quantity": item.quantity,
            "item_total": item.total_price,
            "cart_total": total
        })
