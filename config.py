# class Config:
#     #  Kết nối đến PostgreSQL hiện tại của bạn (shop_db)
#     SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123456@localhost:5433/shop_db"



class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://shop:123456@localhost:5433/shop_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    

# import os

# class Config:
#     SQLALCHEMY_DATABASE_URI = "postgresql://shop:EbwomBvht9ZjpqrnCbmjKbLz2udlK0EN@dpg-d46sdpk9c44c738n5aj0-a/shop_db_ak4d"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# class Config:
#     SQLALCHEMY_DATABASE_URI = "postgresql://shop:cv1sz5CwD75aInU6z5mHmzJ8Gc5y3YOr@dpg-d5pjk9juibrs73d24m00-a/shop_db_qhnd"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

