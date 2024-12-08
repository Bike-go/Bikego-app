import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from flask import current_app

# Helper function to send an email
def send_email(to_email, subject, html_body):
    sender_email = Config.SENDER_EMAIL
    sender_password = Config.SENDER_PASSWORD

    # Create MIME email
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    # Send email using SMTP
    try:
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
            print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

# Function to send registration email
def send_registration_email(email, token):
    url_in_email = Config.URL_IN_EMAIL
    url = f"{url_in_email}/verify-email/{token}"

    try:
        template_path = os.path.join(current_app.root_path, 'static', 'html', 'registration.html')
        with open(template_path, "r", encoding="utf-8") as file:
            body = file.read()
        body = body.replace("{{URL}}", url)
    except FileNotFoundError:
        print("Registration email template not found.")
        return

    send_email(email, "Bikego: Registration", body)

# Function to send reset email (two emails sent in this function)
def send_reset_email(email, email_new, token):
    url_in_email = Config.URL_IN_EMAIL
    url = f"{url_in_email}/verify-email/{token}"

    try:
        template_path_verification = os.path.join(current_app.root_path, 'static', 'html', 'verification.html')
        template_path_info = os.path.join(current_app.root_path, 'static', 'html', 'emailInfo.html')

        with open(template_path_verification, "r", encoding="utf-8") as file:
            body_verification = file.read()
        with open(template_path_info, "r", encoding="utf-8") as file:
            body_info = file.read()

        body_verification = body_verification.replace("{{URL}}", url)
    except FileNotFoundError:
        print("Reset email template not found.")
        return

    send_email(email_new, "Bikego: Email verification", body_verification)
    send_email(email, "Bikego: Email change", body_info)

# Function to send password change email
def send_password_change(email, token):
    url_in_email = Config.URL_IN_EMAIL
    url = f"{url_in_email}/change-password/{token}"

    try:
        template_path = os.path.join(current_app.root_path, 'static', 'html', 'passwordChange.html')
        with open(template_path, "r", encoding="utf-8") as file:
            body = file.read()
        body = body.replace("{{URL}}", url)
    except FileNotFoundError:
        print("Password change email template not found.")
        return

    send_email(email, "Bikego: Change password", body)

# Function to send successfully changed password email
def send_successfully_password_change(email):
    try:
        template_path = os.path.join(current_app.root_path, 'static', 'html', 'successfulyPasswordChange.html')
        with open(template_path, "r", encoding="utf-8") as file:
            body = file.read()
    except FileNotFoundError:
        print("Successfully changed password email template not found.")
        return

    send_email(email, "Bikego: Successfully changed password", body)