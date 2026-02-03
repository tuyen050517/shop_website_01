from flask import render_template

class ProductInfoController:
    @staticmethod
    def show_info():
        return render_template("product_info.html")
