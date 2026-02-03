# chat_routes.py
from flask import Blueprint, request, jsonify
from controllers.chat_controller import handle_chat_message

chat_bp = Blueprint("chat_bp", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    reply = handle_chat_message(user_message)
    return jsonify(reply)  