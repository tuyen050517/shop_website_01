from flask import Blueprint
from controllers.product_info_controller import ProductInfoController

product_info_bp = Blueprint("product_info_bp", __name__)

@product_info_bp.route("/product-info")
def product_info():
    return ProductInfoController.show_info()
