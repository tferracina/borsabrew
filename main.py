from pathlib import Path
import click # type: ignore

from utils import load_config, parse_order, add_order

current_dir = Path.cwd()
config = load_config()

@click.group()
def borsabrew():
    """Morning stock updates"""

@click.command()
@click.argument('order')
def listen(order):
    """Listen for stock orders and parse them"""
    pattern = config["pattern"]
    try:
        order_dict = parse_order(pattern, order)
        add_order(order_dict)

    except Exception as e:
        print(f"Error occurred: {e}")


borsabrew.add_command(listen)

if __name__ == "__main__":
    borsabrew()