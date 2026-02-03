from flask import Blueprint, request
from controllers.order_controller import OrderController

order_bp = Blueprint("order_bp", __name__)

@order_bp.route("/checkout")
def checkout():
    return OrderController.checkout()

@order_bp.route("/confirm_order", methods=["POST"])
def confirm_order():
    payment_method = request.form.get("payment_method")
    return OrderController.confirm_order(payment_method)

# Thêm route này để khi bấm Thanh toán qua MoMo trên giao diện hoạt động
@order_bp.route("/momo_payment")
def momo_payment():
    # Gọi xử lý tạo link thanh toán từ controller
    return OrderController.confirm_order("MoMo")

@order_bp.route("/momo_return", methods=["GET", "POST"])
def momo_return():
    return OrderController.momo_return()

# Thêm route IPN để MoMo gọi về 
@order_bp.route("/momo_ipn", methods=["POST"])
def momo_ipn():
    return OrderController.momo_ipn()

@order_bp.route("/success")
def success():
    return OrderController.success()
