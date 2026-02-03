from flask import render_template, request, flash, redirect, url_for

class ContactController:
    @staticmethod
    def show_contact():
        return render_template("contact.html")

    @staticmethod
    def submit_contact():
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        
        print(f" Liên hệ mới: {name} ({email}) - Nội dung: {message}")

        flash(" Cảm ơn bạn đã liên hệ với MHTHM! Chúng tôi sẽ phản hồi sớm nhất.", "success")
        return redirect(url_for("contact_bp.contact"))
