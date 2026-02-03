from flask import Blueprint
from controllers.product_controller import ProductController

product_bp = Blueprint("product_bp", __name__)

@product_bp.route("/product/<int:id>")
def product_detail(id):
    return ProductController.product_detail(id)


@product_bp.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    return ProductController.add_to_cart(id)
