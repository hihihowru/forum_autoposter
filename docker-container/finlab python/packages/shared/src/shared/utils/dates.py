from datetime import datetime

def today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")