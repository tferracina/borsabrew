import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import datetime

from utils import (load_config, BORSA_FILE, calculate_performance,
                    calculate_portfolio, get_stock_data)

config = load_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_brew():
    """send the daily brew"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    try:             
        sender_email = config["sender_email"]
        sender_password = config["sender_password"]
        receiver_email = config["receiver_email"]

        # SMTP Server and port no. for gmail.com
        gmail_server = "smtp.gmail.com"
        gmail_port = 587

        # Create a multipart message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = f"Borsa Brew del {today}"

        # Read stock data
        if not BORSA_FILE.exists():
            logger.error("Borsa file not found")
            return
        with BORSA_FILE.open("r", encoding="utf8") as f:
            stocks = json.load(f)

        # Get current stock prices
        stock_names = [stock["stock_name"] for stock in stocks]
        current_prices = get_stock_data(stock_names)

        # Calculate performance for each stock and update the stocks list
        for stock in stocks:
            stock_name = stock["stock_name"]
            current_price = current_prices.get(stock_name)
            if current_price is not None:
                stock["current_price"] = current_price
                stock["performance"] = calculate_performance(stock["price"], current_price)
            else:
                stock["current_price"] = None
                stock["performance"] = None

        # Calculate overall portfolio performance
        portfolio_performance = calculate_portfolio(stocks)

        # compose email text
        email_text = "Good morning! Here is your performance for today:\n"
        for stock in stocks:
            email_text += f"{stock['stock_name']}:\n"
            email_text += f"  Bought: {stock['quantity']} shares at ${stock['price']:.2f}\n"
            
            if stock['current_price'] is not None:
                email_text += f"Current Price: ${stock['current_price']:.2f}\n"
                email_text += f"Performance: {stock['performance']:.2f}%\n"
            else:
                email_text += "Current Price: Unable to fetch\n"
                email_text += "Performance: Unable to calculate\n"
            
            email_text += "\n"

        email_text += f"Overall Portfolio Performance: {portfolio_performance:.2f}%\n"

        message.attach(MIMEText(email_text, "plain"))

        # establish connection and send email
        with smtplib.SMTP(gmail_server, gmail_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logger.info("Email sent successfully")

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed. Check your email/password.")
    except smtplib.SMTPException as e:
        logger.error("An error occurred while sending the email: %s", e)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON from borsa.json")
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)


if __name__ == "__main__":
    send_brew()
