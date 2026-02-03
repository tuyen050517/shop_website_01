from flask import Flask, jsonify, request
from config import Config
from models.models import db
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.product_info_routes import product_info_bp
from routes.contact_routes import contact_bp
from routes.admin_routes import admin_bp
from routes.chat_routes import chat_bp

from flask_cors import CORS
import os

# =============================
#  Cấu hình Flask App
# =============================
app = Flask(__name__)
app.config.from_object(Config)
app.config["SECRET_KEY"] = "mht-shop-secret-key"

# Cấu hình upload ảnh sản phẩm
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

# Cho phép frontend truy cập API
CORS(app)

# Gắn Flask app vào SQLAlchemy
db.init_app(app)

# =============================
#  🔥 TẠO BẢNG DATABASE (BẮT BUỘC)
# =============================
with app.app_context():
    db.create_all()

# =============================
#  Đăng ký các Blueprint
# =============================
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(product_info_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(order_bp, url_prefix="/order")

# =============================
#  Chạy Flask (dùng Render PORT)
# =============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
