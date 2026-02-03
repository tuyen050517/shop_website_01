
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from datetime import datetime
from models.models import db, CartItem, Product, Order, User
from utils.payment_helper import get_callback_url
from utils.send_email import send_order_email
import hmac, hashlib, requests


class OrderController:

    # Trang thanh toán (hiển thị giỏ hàng)
    @staticmethod
    def checkout():
        if "user_id" not in session:
            return redirect(url_for("auth_bp.auth"))

        user_id = session["user_id"]
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        if not cart_items:
            flash("Giỏ hàng của bạn đang trống!", "error")
            return redirect(url_for("cart_bp.cart"))

        total = 0
        for item in cart_items:
            product = Product.query.get(item.product_id)
            item.product = product
            item.total_price = product.price * item.quantity
            total += item.total_price

        return render_template("checkout.html", cart_items=cart_items, total=total)

    # Xử lý khi chọn phương thức thanh toán
    @staticmethod
    def confirm_order(payment_method):
        if "user_id" not in session:
            return redirect(url_for("auth_bp.auth"))

        user_id = session["user_id"]
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        if not cart_items:
            flash("Không có sản phẩm nào để thanh toán!", "error")
            return redirect(url_for("cart_bp.cart"))

        total_price = sum(Product.query.get(i.product_id).price * i.quantity for i in cart_items)

        # Nếu thanh toán COD
    
        if payment_method == "COD":

            # Tạo đơn hàng
            new_order = Order(
                user_id=user_id,
                total_amount=total_price,
                payment_method="COD",
                status="Chờ thanh toán",
                created_at=datetime.now(),
            )
            db.session.add(new_order)

            # Lấy danh sách sản phẩm để gửi mail
            items = []
            for i in cart_items:
                p = Product.query.get(i.product_id)
                items.append({
                    "name": p.name,
                    "quantity": i.quantity,
                    "price": p.price
                })

            # XÓA GIỎ HÀNG
            for item in cart_items:
                db.session.delete(item)

            db.session.commit()

            # Gửi email cho COD
            user = User.query.get(user_id)
            send_order_email(user.gmail, items, total_price)

            flash("Đặt hàng thành công (Thanh toán khi nhận hàng).", "success")
            return redirect(url_for("order_bp.success"))

        # Nếu thanh toán bằng MoMo
        elif payment_method == "MoMo":
            endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
            partnerCode = "MOMO"
            accessKey = "F8BBA842ECF85"
            secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
            orderInfo = "Thanh toán MOMO đơn hàng MHTMHShop"

            redirectUrl = get_callback_url('order_bp.momo_return')
            ipnUrl = get_callback_url('order_bp.momo_ipn')

            amount = str(int(total_price))
            orderId = datetime.now().strftime("%Y%m%d%H%M%S")
            requestId = orderId
            requestType = "captureWallet"

            rawSignature = (
                f"accessKey={accessKey}&amount={amount}&extraData=&ipnUrl={ipnUrl}"
                f"&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}"
                f"&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"
            )
            signature = hmac.new(secretKey.encode('utf-8'), rawSignature.encode('utf-8'), hashlib.sha256).hexdigest()

            data = {
                "partnerCode": partnerCode,
                "accessKey": accessKey,
                "requestId": requestId,
                "amount": amount,
                "orderId": orderId,
                "orderInfo": orderInfo,
                "redirectUrl": redirectUrl,
                "ipnUrl": ipnUrl,
                "extraData": "",
                "requestType": requestType,
                "signature": signature,
            }

            try:
                res = requests.post(endpoint, json=data, timeout=10)
                result = res.json()
                if result.get("resultCode") == 0:
                    return redirect(result["payUrl"])
                else:
                    flash(f"Lỗi MoMo: {result.get('message', 'Không rõ')}", "error")
            except Exception as e:
                flash("Lỗi kết nối MoMo!", "error")
                print("MoMo API Error:", e)

            return redirect(url_for("cart_bp.cart"))

    # MoMo gửi POST về đây (IPN - server-to-server)
    @staticmethod
    def momo_ipn():
        data = request.get_json(silent=True) or {}
        print("MoMo IPN nhận được:", data)

        orderId = data.get("orderId")
        resultCode = str(data.get("resultCode"))

        if resultCode == "0":
            print(f"IPN: Thanh toán thành công cho order {orderId}")
        else:
            print(f"IPN: Thanh toán thất bại {orderId}")

        return jsonify({"message": "ok"}), 200

    # Xử lý khi MoMo redirect về trình duyệt
    @staticmethod
    def momo_return():
        resultCode = request.args.get("resultCode")
        orderId = request.args.get("orderId")

        # Ngăn tạo đơn trùng
        if session.get("momo_order_id") == orderId:
            return redirect(url_for("order_bp.success"))

        if resultCode == "0":
            if "user_id" not in session:
                flash("Vui lòng đăng nhập!", "error")
                return redirect(url_for("auth_bp.auth"))

            user_id = session["user_id"]
            cart_items = CartItem.query.filter_by(user_id=user_id).all()
            if not cart_items:
                flash("Giỏ hàng trống!", "error")
                return redirect(url_for("cart_bp.cart"))

            total_price = sum(Product.query.get(i.product_id).price * i.quantity for i in cart_items)

            # Tạo đơn hàng
            order = Order(
                user_id=user_id,
                total_amount=total_price,
                payment_method="MoMo",
                status="Đã thanh toán",
                created_at=datetime.now(),
            )
            db.session.add(order)
            db.session.flush()  # Lấy order.id


            # Xóa giỏ hàng
            for item in cart_items:
                db.session.delete(item)

            db.session.commit()

            # GỬI EMAIL XÁC NHẬN ĐƠN HÀNG
            user = User.query.get(user_id)

            items = []
            for i in cart_items:
                p = Product.query.get(i.product_id)
                items.append({
                    "name": p.name,
                    "quantity": i.quantity,
                    "price": p.price
                })

            send_order_email(user.gmail, items, total_price)


            session["momo_order_id"] = orderId
            session["last_order_id"] = order.id

            flash("Thanh toán MoMo thành công!", "success")
            return redirect(url_for("order_bp.success"))

        else:
            flash("Thanh toán thất bại hoặc bị hủy.", "error")
            return redirect(url_for("cart_bp.cart"))

    @staticmethod
    def success():
        session.pop("momo_order_id", None)
        session.pop("momo_paid", None)

        order_id = session.pop("last_order_id", None)
        if order_id:
            order = Order.query.get(order_id)
            return render_template("success.html", order=order)
        return render_template("success.html")
