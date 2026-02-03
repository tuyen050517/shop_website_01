

import os
from dotenv import load_dotenv
import resend
from threading import Thread

# Load ENV
load_dotenv()

# Lấy API KEY
resend.api_key = os.getenv("RESEND_API_KEY")

def _send(email, otp):
    params = {
        "from": "OTP Service <no-reply@mhtmh.id.vn>",
        "to": [email],
        "subject": "Mã OTP Xác Nhận",
        "text": f"OTP của bạn là: {otp}\nOTP có hiệu lực trong 5 phút.",
    }

    try:
        resend.Emails.send(params)
        print("Đã gửi OTP đến:", email)
    except Exception as e:
        print("Lỗi gửi email Resend:", e)


def send_otp_email(email, otp):
    Thread(target=_send, args=(email, otp)).start()


    # send gmail oder
def _send_order(email, items, total_price):
    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{item['name']}</td>
            <td>{item['quantity']}</td>
            <td>{item['price']:,} VND</td>
        </tr>
        """

    html = f"""
    <h2 style='color:#4CAF50;'> Đặt hàng thành công!</h2>
    <p>Cảm ơn bạn đã mua hàng. Đây là chi tiết đơn hàng:</p>

    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
        <tr style="background:#f2f2f2;">
            <th>Sản phẩm</th>
            <th>Số lượng</th>
            <th>Giá</th>
        </tr>
        {rows}
    </table>

    <p><b>Tổng tiền: {total_price:,} VND</b></p>
    <p>Chúc bạn một ngày tốt lành </p>
    """

    params = {
        "from": "MHTMHshop <no-reply@mhtmh.id.vn>",
        "to": [email],
        "subject": "Xác nhận đặt hàng thành công",
        "html": html,
    }

    try:
        resend.Emails.send(params)
        print("Đã gửi email đơn hàng đến:", email)
    except Exception as e:
        print("Lỗi gửi email đơn hàng:", e)


def send_order_email(email, items, total_price):
    Thread(target=_send_order, args=(email, items, total_price)).start()