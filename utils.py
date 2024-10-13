import json
from pathlib import Path
import re
from typing import Dict, Any, List


current_dir = Path.cwd()
CONFIG_FILE = current_dir / "config.json"
BORSA_FILE = current_dir / "borsa.json"


def load_config() -> Dict[str, Any]:
    """
    Load configuration or create default if not exists.   
    :return: Dictionary containing configuration
    """ 
    if not CONFIG_FILE.exists():
        default_config = {
            "update_time": "08:00",
            "sender_email": "send@gmail.com",
            "sender_password": "password",
            "receiver_email": "receive@gmail.com",
            "pattern": r"Ord Sh, (.*) has been filled on (\d{1,2} \w+ \d{4}) (\d{2}:\d{2}:\d{2})\. Filled price: USD (\d+\.\d+)\. Filled Qty: (\d+)"
        }
        with CONFIG_FILE.open('w', encoding='utf8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config
    else:
        with CONFIG_FILE.open('r', encoding="utf8") as f:
            return json.load(f)


def parse_order(pattern: str, order: str) -> Dict[str, Any]:
    """
    Parse order string using the given pattern.
    :param pattern: Regex pattern to match the order
    :param order: Order string to parse
    :return: Dictionary containing parsed order details
    :raises ValueError: If order cannot be parsed
    """
    match = re.search(pattern, order)
    if match:
        return {
            "stock_name": match.group(1),
            "date": match.group(2),
            "time": match.group(3),
            "price": float(match.group(4)),
            "quantity": int(match.group(5))
            }
    else:
        raise ValueError("order could not be parsed")


def add_order(order_dict: Dict[str, Any]) -> None:
    """
    Adds stock to BORSA

    :param order_dict: Dictionary containing order details
    :raises IOError: If there's an error writing the file
    """
    try:
        if not BORSA_FILE.exists():
            orders: List[Dict[str, Any]] = []
        else:
            with BORSA_FILE.open('r', encoding='utf8') as f:
                orders = json.load(f)
        
        if not isinstance(orders, list):
            orders = []

        orders.append(order_dict)

        with open(BORSA_FILE, 'w', encoding='utf8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=4)
    except IOError as e:
        raise IOError("error writing to BORSA file: %s", e)
