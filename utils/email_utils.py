import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

def send_verification_email(email, token):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    subject = "Email Verification"
    body = f"Please verify your email by clicking the link: http://localhost:5000/user/verify-email/{token}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, email, message)
    except Exception as e:
        print(f"Error sending email: {e}")

def send_refresh_password_email(email, token):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    subject = "Password Change Request"
    body = f"To change your password, please click the link: http://yourdomain.com/change-password/{token}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, email, message)
    except Exception as e:
        print(f"Error sending email: {e}")