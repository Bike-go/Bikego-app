import smtplib
from dotenv import load_dotenv
from ..app import app

load_dotenv()

def send_verification_email(email, token):
    sender_email = app.config["SENDER_EMAIL"]
    sender_password = app.config["SENDER_PASSWORD"]
    url_in_email = app.config["URL_IN_EMAIL"]
    subject = "Email Verification"
    body = f"Please verify your email by clicking the link: {url_in_email}/verify-email/{token}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, email, message)
    except Exception as e:
        print(f"Error sending email: {e}")

def send_refresh_password_email(email, token):
    sender_email = app.config["SENDER_EMAIL"]
    sender_password = app.config["SENDER_PASSWORD"]
    url_in_email = app.config["URL_IN_EMAIL"]
    subject = "Password Change Request"
    body = f"To change your password, please click the link: {url_in_email}/change-password/{token}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, email, message)
    except Exception as e:
        print(f"Error sending email: {e}")

def send_welcome_email(email):
    sender_email = app.config["SENDER_EMAIL"]
    sender_password = app.config["SENDER_PASSWORD"]
    subject = "Welcome to our platform!"
    body = "Thank you for joining our platform!"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, email, message)
    except Exception as e:
        print(f"Error sending email: {e}")