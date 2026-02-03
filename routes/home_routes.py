from flask import Blueprint, request
from controllers.home_controller import HomeController

home_bp = Blueprint("home_bp", __name__)

@home_bp.route("/")
def home():
    return HomeController.show_home()

@home_bp.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("q", "")
    return HomeController.search_products(keyword)
