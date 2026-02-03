
from flask import request, url_for
from urllib.parse import urljoin

def get_callback_url(endpoint):
    """
    Tạo URL callback động cho mọi môi trường
    endpoint phải là 'order_bp.momo_return', 'order_bp.momo_ipn', ...
    """
    host = request.host

    # Xác định scheme
    if host.startswith('localhost') or host.startswith('127.0.0.1'):
        scheme = 'http'
    else:
        scheme = 'https'

    base_url = f"{scheme}://{host}"
    return urljoin(base_url + '/', url_for(endpoint)) 