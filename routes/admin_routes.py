from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from controllers.admin_controller import AdminController

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# LOGIN / LOGOUT

@admin_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return AdminController.login(request.form["username"], request.form["password"])
    return render_template("admin_login.html")


@admin_bp.route("/dashboard")
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_bp.login"))
    return render_template("admin_dashboard.html", users=AdminController.get_all_users())


@admin_bp.route("/logout")
def logout():
    return AdminController.logout()


# SẢN PHẨM 

@admin_bp.route("/products")
def products():
    if "admin_id" not in session:
        return redirect(url_for("admin_bp.login"))
    page = request.args.get("page", 1, type=int)
    products, current_page, total_pages = AdminController.get_products_paginated(page)
    return render_template("admin_products.html", products=products, current_page=current_page, total_pages=total_pages)


@admin_bp.route("/products/add", methods=["POST"])
def add_product():
    AdminController.handle_add_product(request)
    flash(" Đã thêm sản phẩm mới!", "success")
    return redirect(url_for("admin_bp.products"))


@admin_bp.route("/products/edit/<int:pid>")
def edit_product(pid):
    product = AdminController.get_product_by_id(pid)
    if not product:
        flash("Không tìm thấy sản phẩm!", "danger")
        return redirect(url_for("admin_bp.products"))
    return render_template("admin_edit_product.html", product=product)


@admin_bp.route("/products/update/<int:pid>", methods=["POST"])
def update_product(pid):
    AdminController.handle_update_product(request, pid)
    flash(" Đã cập nhật sản phẩm!", "info")
    return redirect(url_for("admin_bp.products"))


@admin_bp.route("/products/delete/<int:pid>")
def delete_product(pid):
    AdminController.delete_product(pid)
    flash(" Đã xóa sản phẩm!", "warning")
    return redirect(url_for("admin_bp.products"))


# ĐƠN HÀNG

@admin_bp.route("/orders")
def orders():
    if "admin_id" not in session:
        return redirect(url_for("admin_bp.login"))
    return render_template("admin_orders.html", orders=AdminController.get_all_orders())


@admin_bp.route("/orders/confirm/<int:order_id>")
def confirm_order(order_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_bp.login"))
    if AdminController.confirm_payment(order_id):
        flash(" Đã xác nhận thanh toán đơn hàng!", "success")
    else:
        flash(" Không thể xác nhận!", "warning")
    return redirect(url_for("admin_bp.orders"))
