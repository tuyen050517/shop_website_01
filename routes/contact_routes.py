from flask import Blueprint
from controllers.contact_controller import ContactController

contact_bp = Blueprint("contact_bp", __name__)

@contact_bp.route("/contact")
def contact():
    return ContactController.show_contact()

@contact_bp.route("/contact", methods=["POST"])
def contact_submit():
    return ContactController.submit_contact()
