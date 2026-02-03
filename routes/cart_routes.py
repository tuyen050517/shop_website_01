from flask import Blueprint
from controllers.cart_controller import CartController

# Khai báo blueprint
cart_bp = Blueprint("cart_bp", __name__)

# Route hiển thị giỏ hàng 
@cart_bp.route("/cart", endpoint="cart")
def show_cart():
    return CartController.show_cart()

# Route xóa sản phẩm trong giỏ hàng
@cart_bp.route("/cart/delete/<int:product_id>", methods=["POST"], endpoint="delete_item")
def delete_item(product_id):
    return CartController.delete_item(product_id)

#  Route cập nhật số lượng 
@cart_bp.route("/update_quantity/<int:product_id>/<string:action>", methods=["POST"], endpoint="update_quantity")
def update_quantity(product_id, action):
    return CartController.update_quantity(product_id, action)

