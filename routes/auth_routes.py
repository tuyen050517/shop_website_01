from flask import Blueprint, render_template, request, redirect, url_for
from controllers.auth_controller import AuthController

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# Trang login/register
@auth_bp.route("/", methods=["GET"])
def auth():
    return render_template("auth.html")

# ĐĂNG KÝ → GỬI OTP

@auth_bp.route("/register", methods=["POST"])
def register():
    fullname = request.form.get("fullname")
    gmail = request.form.get("gmail")
    username = request.form.get("username")
    password = request.form.get("password")
    return AuthController.register(fullname, gmail, username, password)



# VERIFY OTP ĐĂNG KÝ (HIỂN THỊ)

@auth_bp.route("/verify-register-otp", methods=["GET"])
def verify_register_page():
    return render_template(
        "verify_otp.html",
        action_url=url_for("auth_bp.verify_register"),
        resend_url=url_for("auth_bp.resend_otp")
    )

# VERIFY OTP ĐĂNG KÝ (XỬ LÝ)

@auth_bp.route("/verify-register-otp", methods=["POST"])
def verify_register():
    otp = request.form.get("otp")
    return AuthController.verify_register_otp(otp)

# ĐĂNG NHẬP
@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    return AuthController.login(username, password)

# ĐĂNG XUẤT

@auth_bp.route("/logout")
def logout():
    return AuthController.logout()

# RESEND OTP ĐĂNG KÝ

@auth_bp.route("/resend-otp", methods=["GET"])
def resend_otp():
    return AuthController.resend_otp()



# QUÊN MẬT KHẨU → NHẬP GMAIL

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    return AuthController.forgot_password()


# VERIFY OTP RESET PASSWORD (HIỂN THỊ)

@auth_bp.route("/verify-forgot-otp", methods=["GET"])
def verify_forgot_page():
    return render_template(
        "verify_otp.html",
        action_url=url_for("auth_bp.verify_forgot"),
        resend_url=url_for("auth_bp.resend_forgot_otp")
    )

# VERIFY OTP RESET PASSWORD 
@auth_bp.route("/verify-forgot-otp", methods=["POST"])
def verify_forgot():
    otp = request.form.get("otp")
    return AuthController.verify_forgot_otp(otp)

# RESEND OTP RESET PASSWORD

@auth_bp.route("/resend-forgot-otp", methods=["GET"])
def resend_forgot_otp():
    return AuthController.resend_forgot_otp()

# ĐẶT LẠI MẬT KHẨU

@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    return AuthController.reset_password()
