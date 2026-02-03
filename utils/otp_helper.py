
import random
from datetime import datetime, timedelta
from models.models import db, OtpRegister
from utils.send_email import send_otp_email

def generate_or_update_otp(email):

    # gửi OTP trong vòng 60 giây
    otp = OtpRegister.query.filter_by(email=email).first()

    if otp and otp.created_at > datetime.utcnow() - timedelta(seconds=60):
        return False

    otp_code = str(random.randint(100000, 999999))
    expire_at = datetime.utcnow() + timedelta(minutes=5)

    if otp:
        otp.otp_code = otp_code
        otp.expire_at = expire_at
        otp.created_at = datetime.utcnow()
        otp.is_verified = False
    else:
        otp = OtpRegister(
            email=email,
            otp_code=otp_code,
            expire_at=expire_at
        )
        db.session.add(otp)

    db.session.commit()
    send_otp_email(email, otp_code)
    return True


def get_valid_otp(email):
    otp = OtpRegister.query.filter_by(email=email, is_verified=False).first()

    if not otp:
        return None

    if otp.expire_at < datetime.utcnow():
        db.session.delete(otp)
        db.session.commit()
        return None

    return otp


def verify_otp(email, otp_input):
    otp = get_valid_otp(email)
    if not otp:
        return False

    if otp.otp_code != otp_input:
        return False

    # Xóa OTP sau khi dùng
    db.session.delete(otp)
    db.session.commit()

    return True

