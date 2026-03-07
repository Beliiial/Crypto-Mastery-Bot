import hashlib
import hmac
import json
from urllib.parse import parse_qsl

def parse_init_data(init_data: str) -> dict:
    return dict(parse_qsl(init_data, keep_blank_values=True))

def validate_init_data(init_data: str, bot_token: str) -> bool:
    data = parse_init_data(init_data)
    hash_value = data.pop("hash", None)
    if not hash_value:
        return False
    data_check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return calculated_hash == hash_value

def get_user_from_init_data(init_data: str):
    data = parse_init_data(init_data)
    user_json = data.get("user")
    if not user_json:
        return None
    try:
        return json.loads(user_json)
    except Exception:
        return None
