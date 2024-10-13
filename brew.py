import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import logging
import datetime

from utils import load_config, BORSA_FILE

config = load_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_brew():
    """send the daily brew"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    try:             
        sender_email = config["sender_email"]
        sender_password = config["sender_password"]
        print(sender_email, sender_password)
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

        # compose email text
        email_text = "Good morning! Here is your performance for today:\n"
        for stock in stocks:
            email_text += f"{stock['stock_name']} - {stock['quantity']} shares at {stock['price']}\
            \n"

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