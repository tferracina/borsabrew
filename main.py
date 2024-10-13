import logging
import click

from utils import load_config, parse_order, add_order
from brew import send_brew

config = load_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def borsabrew():
    """Morning stock updates"""

@borsabrew.command()
@click.argument('order')
def listen(order: str):
    """Listen for stock orders and parse them"""
    pattern = config["pattern"]
    try:
        order_dict = parse_order(pattern, order)
        add_order(order_dict)
        logger.info("Order processed successfully: %s", order_dict['stock_name'])
    except ValueError as e:
        logger.error("Error parsing order: %s", e)
    except IOError as e:
        logger.error("Error writing to file: %s", e)
    except Exception as e:
        logger.error("Unexpected error occurred: %s", e)

@borsabrew.command()
def brew():
    """Send the daily brew"""
    send_brew()


borsabrew.add_command(listen)
borsabrew.add_command(brew)

if __name__ == "__main__":
    borsabrew()
