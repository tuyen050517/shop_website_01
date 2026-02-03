from flask import render_template
from models.models import Product
from rapidfuzz import fuzz


class HomeController:
    # Hiển thị trang chủ
    @staticmethod
    def show_home():
        iphones = Product.query.filter(Product.category.ilike('%iphone%')).all()
        samsungs = Product.query.filter(Product.category.ilike('%samsung%')).all()
        laptops = Product.query.filter(Product.category.ilike('%laptop%')).all()

        return render_template(
            "home.html",
            iphones=iphones,
            samsungs=samsungs,
            laptops=laptops,
            search_results=None,
            keyword=None
        )

    # Tìm kiếm sản phẩm
    @staticmethod
    def search_products(keyword):
        if not keyword or not keyword.strip():
            return HomeController.show_home()

        keyword = keyword.strip()
        keyword_lower = keyword.lower()
        matched_products = []

        # Lấy tất cả sản phẩm (có thể tối ưu bằng DB query sau)
        all_products = Product.query.all()

        for p in all_products:
            name_lower = p.name.lower()
            # Tìm chính xác hoặc tương đồng 
            if (keyword_lower in name_lower) or (fuzz.partial_ratio(keyword_lower, name_lower) >= 70):
                matched_products.append(p)

        # Xác định keyword hiển thị: có kết quả → ẩn, không có → hiện để người dùng biết
        display_keyword = keyword if not matched_products else ""

        return render_template(
            "home.html",
            search_results=matched_products or None,
            keyword=display_keyword,
            iphones=[],
            samsungs=[],
            laptops=[]
        )