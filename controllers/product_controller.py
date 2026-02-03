from flask import render_template, redirect, url_for, session, jsonify
from models.models import db, Product, CartItem

class ProductController:
    @staticmethod
    def product_detail(id):
        product = Product.query.get_or_404(id)
        return render_template("product_detail.html", product=product)


    @staticmethod
    def add_to_cart(id):
        #  chưa đăng nhập
        if "user_id" not in session:
            product = Product.query.get(id)
            return render_template(
                "auth_required.html",
                message=" Bạn cần đăng nhập để thêm sản phẩm vào giỏ hàng!",
                login_url=url_for("auth_bp.auth"),
                back_url=url_for("product_bp.product_detail", id=id),
                product=product
            )

        # đã đăng nhập
        user_id = session["user_id"]
        product = Product.query.get_or_404(id)

        item = CartItem.query.filter_by(user_id=user_id, product_id=id).first()
        if item:
            item.quantity += 1
        else:
            item = CartItem(user_id=user_id, product_id=id, quantity=1)
            db.session.add(item)

        db.session.commit()

        # hiển thị thông báo nhỏ
        return jsonify({"message": f" Đã thêm {product.name} vào giỏ hàng!"})
