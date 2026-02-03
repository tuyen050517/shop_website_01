from flask import session, jsonify
from models.models import db, Product
import re, unicodedata, random
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

# Mapping thương hiệu

BRAND_MAP = {
    "iphone": ["ip", "ifone", "ai phôn", "ai phone"],
    "samsung": ["glx", "galaxy", "sam sung"],
    "asus": ["asua", "may asus", "laptop asus"],
    "macbook": ["mac", "mác búc", "mắc búc", "apple laptop"],
    "laptop": ["lap", "latop", "may tinh xach tay"]
}


#  Cache sản phẩm

@lru_cache(maxsize=1)
def get_all_products():
    products = Product.query.all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price or 0),
            "image_url": p.image_url,
            "description": p.description or "",
            "category": (p.category or "").lower(),
            "brand": (p.brand or "").lower(),
            "chipset": (p.chipset or "").lower(),
            "ram": (p.ram or "").lower(),
            "storage": (p.storage or "").lower(),
            "battery": p.battery or 0,
            "screen_size": p.screen_size or 0,
            "weight": p.weight or 0,
            "performance_score": p.performance_score or 0,
            "release_year": p.release_year or 0,
        }
        for p in products
    ]


#  Chuẩn hóa text

def normalize(text: str):
    if not text:
        return ""
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    for k, vs in BRAND_MAP.items():
        for v in vs:
            t = t.replace(v, k)
    return re.sub(r"\s+", " ", t).strip()


#  Nhận diện thương hiệu

def extract_brand(msg, products):
    msg = normalize(msg)
    brands = {p["brand"] for p in products if p.get("brand")}
    for k, vs in BRAND_MAP.items():
        if k in msg or any(v in msg for v in vs):
            return k if k in brands else None
    for b in brands:
        if b in msg:
            return b
    return None

#  Tìm sản phẩm thông minh (TF-IDF + fuzzy)

def find_product(user_msg, products):
    msg = normalize(user_msg)
    if not msg:
        return None

    texts = [
        normalize(f"{p['name']} {p['brand']} {p['chipset']} {p['ram']} {p['storage']} {p['description']}")
        for p in products
    ]
    try:
        vec = TfidfVectorizer().fit_transform(texts + [msg])
        sims = cosine_similarity(vec[-1], vec[:-1]).flatten()
    except Exception:
        sims = [0] * len(products)

    best = max(
        ((i, sims[i] * 0.7 + SequenceMatcher(None, msg, normalize(products[i]['name'])).ratio() * 0.3)
         for i in range(len(products))),
        key=lambda x: x[1], default=(None, 0)
    )
    return products[best[0]] if best[1] > 0.25 else None


# Xử lý đặc biệt (đắt/rẻ/pin/hiệu năng…)

def find_special_case(msg, products):
    msg = normalize(msg)
    brand = extract_brand(msg, products)
    pool = [p for p in products if not brand or brand in (p["brand"] or "")]

    if not pool:
        return None

    # Đắt / Rẻ
    if any(k in msg for k in ["dat nhat", "mac nhat", "cao nhat", "dắt nhat"]):
        p = max(pool, key=lambda x: x["price"])
        return f"Sản phẩm đắt nhất{(' của ' + brand) if brand else ''} là {p['name']} ({int(p['price']):,}đ)."
    if "re nhat" in msg:
        p = min(pool, key=lambda x: x["price"])
        return f"Sản phẩm rẻ nhất{(' của ' + brand) if brand else ''} là {p['name']} ({int(p['price']):,}đ)."

    # Pin trâu
    if "pin" in msg and any(k in msg for k in ["tot nhat", "trau"]):
        p = max(pool, key=lambda x: x["battery"])
        return f"Sản phẩm có pin trâu nhất{(' của ' + brand) if brand else ''} là {p['name']} ({p['battery']} mAh)."

    # Hiệu năng cao nhất
    if "hieu nang" in msg or "manh" in msg:
        p = max(pool, key=lambda x: x["performance_score"])
        return f"Sản phẩm mạnh nhất{(' của ' + brand) if brand else ''} là {p['name']} ({p['performance_score']} điểm)."

    # Mới nhất
    if "moi nhat" in msg or "ra mat" in msg:
        p = max(pool, key=lambda x: x["release_year"])
        return f"Sản phẩm mới nhất{(' của ' + brand) if brand else ''} là {p['name']} (ra mắt {p['release_year']})."

    return None

# So sánh 2 sản phẩm
def compare_products(n1, n2, products):
    p1, p2 = find_product(n1, products), find_product(n2, products)
    if not p1 or not p2:
        return "Không tìm thấy sản phẩm để so sánh."

    attrs = [("performance_score", "hiệu năng"), ("battery", "pin"), ("price", "giá")]
    diff = [label for key, label in attrs if p1.get(key) != p2.get(key)]
    better = p1 if p1["performance_score"] >= p2["performance_score"] else p2

    return (
        f"So sánh {p1['name']} và {p2['name']}:\n"
        f"- {p1['name']}: {int(p1['price']):,}đ, chip {p1['chipset']}, RAM {p1['ram']}, pin {p1['battery']}mAh.\n"
        f"- {p2['name']}: {int(p2['price']):,}đ, chip {p2['chipset']}, RAM {p2['ram']}, pin {p2['battery']}mAh.\n"
        f"➡️ {better['name']} tốt hơn (xét {', '.join(diff) if diff else 'tổng thể'})."
    )

#  Xử lý tin nhắn chính
def handle_chat_message(user_message):
    products = get_all_products()
    if not products:
        return {"reply": "Không có dữ liệu sản phẩm.", "history": []}

    msg = normalize(user_message)
    history = session.get("chat_history", [])
    reply = None

    # So sánh
    if m := re.findall(r"so sanh (.+?) (?:va|vs|voi|với) (.+)", msg):
        reply = compare_products(m[0][0], m[0][1], products)
    # Trường hợp đặc biệt (đắt, rẻ, pin…)
    elif special := find_special_case(user_message, products):
        reply = special
    # Giá cụ thể
    elif re.search(r"(gia|bao nhieu|tien|gia ban)", msg):
        p = find_product(user_message, products)
        if p:
            reply = f"{p['name']} có giá {int(p['price']):,}đ."
        else:
            brand = extract_brand(msg, products)
            if brand:
                reply = find_special_case(f"re nhat {brand}", products)
            else:
                reply = "Không rõ sản phẩm bạn hỏi."
    # Năm ra mắt
    elif re.search(r"(ra mat|nam nao|năm nào)", msg):
        p = find_product(user_message, products)
        reply = f"{p['name']} ra mắt năm {p['release_year']}." if p else "Không rõ sản phẩm bạn hỏi."
    # Thông tin chung
    else:
        p = find_product(user_message, products)
        reply = (
            f"{p['name']} giá {int(p['price']):,}đ, chip {p['chipset']}, RAM {p['ram']}, pin {p['battery']}mAh, hiệu năng {p['performance_score']} điểm."
            if p else "Xin lỗi, tôi chưa hiểu sản phẩm bạn nói đến."
        )

    history.append({"user": user_message, "bot": reply})
    session["chat_history"] = history
    return {"reply": reply, "history": history}
