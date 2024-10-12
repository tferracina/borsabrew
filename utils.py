import json
from pathlib import Path
import re


current_dir = Path.cwd()
CONFIG_FILE = current_dir / "config.json"
BORSA_FILE = current_dir / "borsa.json"


def load_config():
    if not CONFIG_FILE.exists():
        default_config = {
            "update_time": "08:00",
            "email": "your_email@example.com",
            "pattern": r"Ord Sh, (.*) has been filled on (\d{1,2} \w+ \d{4}) (\d{2}:\d{2}:\d{2})\. Filled price: USD (\d+\.\d+)\. Filled Qty: (\d+)"
        }
        with open(CONFIG_FILE, 'w', encoding='utf8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config
    else:
        # If the file exists, load the configuration
        with open(CONFIG_FILE, 'r', encoding="utf8") as f:
            current_config = json.load(f)
        return current_config
    

def parse_order(pattern, order):
    match = re.search(pattern, order)
    if match:
        order_dict = {
            "stock_name": match.group(1),
            "date": match.group(2),
            "time": match.group(3),
            "price": float(match.group(4)),
            "quantity": int(match.group(5))
            }
        return order_dict
    else:
        print("order was unable to be parsed")


def add_order(order_dict):
    """Adds stock to BORSA"""
    if not BORSA_FILE.exists():
        with open(BORSA_FILE, 'w', encoding='utf8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    with open(BORSA_FILE, 'r', encoding='utf8') as f:
        orders = json.load(f)
    
    if not isinstance(orders, list):
        orders = []

    orders.append(order_dict)

    with open(BORSA_FILE, 'w', encoding='utf8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)

