from flask import render_template, request, redirect, url_for, flash, session
from models.models import db, User
from utils.otp_helper import generate_or_update_otp, verify_otp
from utils.send_email import send_otp_email
import random

class AuthController:

    #   ĐĂNG KÝ GỬI OTP

    @staticmethod
    def register(fullname, gmail, username, password):
        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại!", "error")
            return redirect(url_for("auth_bp.auth"))

        if User.query.filter_by(gmail=gmail).first():
            flash("Gmail đã được sử dụng!", "error")
            return redirect(url_for("auth_bp.auth"))

        # Gửi OTP qua helper
        generate_or_update_otp(gmail)

        # Lưu thông tin tạm
        session["pending_user"] = {
            "fullname": fullname,
            "gmail": gmail,
            "username": username,
            "password": password,
        }

        return render_template(
            "verify_otp.html",
            action_url=url_for("auth_bp.verify_register"),
            resend_url=url_for("auth_bp.resend_otp"),
        )

    #  VERIFY OTP ĐĂNG KÝ

    @staticmethod
    def verify_register_otp(otp_input):
        pending = session.get("pending_user")

        if not pending:
            flash("Không tìm thấy dữ liệu đăng ký!", "error")
            return redirect(url_for("auth_bp.auth"))

        gmail = pending["gmail"]

        if not verify_otp(gmail, otp_input):
            flash("OTP không đúng hoặc đã hết hạn!", "error")
            return redirect(url_for("auth_bp.verify_register_page"))

        # Tạo user
        user = User(
            fullname=pending["fullname"],
            gmail=pending["gmail"],
            username=pending["username"],
            password=pending["password"],
         
        )

        db.session.add(user)
        db.session.commit()

        session.pop("pending_user", None)

        flash("Đăng ký thành công!", "success")
        return redirect(url_for("auth_bp.auth"))

    #  GỬI LẠI OTP ĐĂNG KÝ

    @staticmethod
    def resend_otp():
        pending = session.get("pending_user")

        if not pending:
            flash("Không tìm thấy dữ liệu đăng ký!", "error")
            return redirect(url_for("auth_bp.auth"))

        result = generate_or_update_otp(pending["gmail"])

        if not result:
            flash("Bạn chỉ được gửi lại OTP sau 60 giây!", "error")
        else:
            flash("OTP mới đã được gửi!", "success")

        return render_template(
            "verify_otp.html",
            action_url=url_for("auth_bp.verify_register"),
            resend_url=url_for("auth_bp.resend_otp"),
        )



    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()

        
        if user and user.password == password:
            session["user_id"] = user.id
            session["user_name"] = user.fullname or user.username  #
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("home_bp.home"))
        else:
            flash("Sai tài khoản hoặc mật khẩu!", "error")
            return redirect(url_for("auth_bp.auth"))
    #  LOGOUT
   
    @staticmethod
    def logout():
        session.clear()
        return redirect(url_for("auth_bp.auth"))

    #  QUÊN MẬT KHẨU
 
    @staticmethod
    def forgot_password():
        if request.method == "GET":
            return render_template("forgot_password.html")

        gmail = request.form.get("gmail")

        if not User.query.filter_by(gmail=gmail).first():
            flash("Email không tồn tại!", "error")
            return redirect(url_for("auth_bp.forgot_password"))

        generate_or_update_otp(gmail)
        session["reset_gmail"] = gmail

        return render_template(
            "verify_otp.html",
            action_url=url_for("auth_bp.verify_forgot"),
            resend_url=url_for("auth_bp.resend_forgot_otp"),
        )

    #  VERIFY FORGOT OTP
   
    @staticmethod
    def verify_forgot_otp(otp_input):
        gmail = session.get("reset_gmail")

        if not gmail:
            flash("Phiên đã hết hạn!", "error")
            return redirect(url_for("auth_bp.forgot_password"))

        if not verify_otp(gmail, otp_input):
            flash("OTP không đúng hoặc đã hết hạn!", "error")
            return redirect(url_for("auth_bp.verify_forgot_page"))

        return redirect(url_for("auth_bp.reset_password"))

    # GỬI LẠI OTP QUÊN MẬT KHẨU

    @staticmethod
    def resend_forgot_otp():
        gmail = session.get("reset_gmail")

        if not gmail:
            flash("Phiên đã hết hạn!", "error")
            return redirect(url_for("auth_bp.forgot_password"))

        generate_or_update_otp(gmail)
        flash("OTP đã được gửi lại!", "success")

        return render_template(
            "verify_otp.html",
            action_url=url_for("auth_bp.verify_forgot"),
            resend_url=url_for("auth_bp.resend_forgot_otp"),
        )
    #  RESET PASSWORD
    @staticmethod
    def reset_password():
        if request.method == "GET":
            return render_template("reset_password.html")

        gmail = session.get("reset_gmail")

        if not gmail:
            flash("Phiên đã hết hạn!", "error")
            return redirect(url_for("auth_bp.forgot_password"))

        new_pass = request.form.get("password")
        if not new_pass or len(new_pass) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự!", "error")
            return render_template("reset_password.html")

        user = User.query.filter_by(gmail=gmail).first()
        if not user:
            flash("Tài khoản không tồn tại!", "error")
            return redirect(url_for("auth_bp.forgot_password"))

    
        user.password = new_pass

        db.session.commit()
        session.pop("reset_gmail", None)

        flash("Đổi mật khẩu thành công!", "success")
        return redirect(url_for("auth_bp.auth"))