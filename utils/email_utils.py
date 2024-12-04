import smtplib
from dotenv import load_dotenv
from config import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def send_verification_email(email, token):
    sender_email = Config.SENDER_EMAIL
    sender_password = Config.SENDER_PASSWORD
    url_in_email = Config.URL_IN_EMAIL

    # Construct the verification link
    verification_link = f"{url_in_email}/users/verify-email/{token}"

    # Email content
    subject = "Email Verification"
    body_plain = f"Please verify your email by clicking the link: {verification_link}"
    body_html = f"""
    <html>
    <body>
        <h1>Verify Your Email</h1>
        <p>Thank you for registering with us! Please verify your email by clicking the link below:</p>
        <p><a href="{verification_link}" target="_blank">Verify Email</a></p>
        <p>If you did not register, please ignore this email.</p>
    </body>
    </html>
    """

    # Create MIME email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = email
    message.attach(MIMEText(body_plain, "plain"))
    message.attach(MIMEText(body_html, "html"))

    try:
        # Connect to SMTP server
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
            print("Verification email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_refresh_password_email(email, token):
    sender_email = Config.SENDER_EMAIL
    sender_password = Config.SENDER_PASSWORD
    url_in_email = Config.URL_IN_EMAIL

    # Construct the password reset link
    reset_link = f"{url_in_email}/users/change-password/{token}"

    # Email content
    subject = "Password Change Request"
    body_plain = f"To change your password, please click the link: {reset_link}"
    body_html = f"""
    <html>
    <body>
        <h1>Password Reset Request</h1>
        <p>We received a request to reset your password. You can do so by clicking the link below:</p>
        <p><a href="{reset_link}" target="_blank">Reset Password</a></p>
        <p>If you didn't request this, please ignore this email.</p>
    </body>
    </html>
    """

    # Create MIME email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = email
    message.attach(MIMEText(body_plain, "plain"))
    message.attach(MIMEText(body_html, "html"))

    try:
        # Connect to SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
            print("Password reset email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_welcome_email(email):
    sender_email = Config.SENDER_EMAIL
    sender_password = Config.SENDER_PASSWORD

    # Email content
    subject = "Welcome to Our Platform!"
    body_plain = "Thank you for joining our platform! We're excited to have you on board."
    body_html = f"""
    <html>
    <body>
        <h1>Welcome to Our Platform!</h1>
        <p>Thank you for joining us! We're thrilled to have you on board and look forward to serving you.</p>
        <p>If you have any questions, feel free to reach out to our support team.</p>
        <p>Enjoy your journey with us!</p>
    </body>
    </html>
    """

    # Create MIME email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = email
    message.attach(MIMEText(body_plain, "plain"))
    message.attach(MIMEText(body_html, "html"))

    try:
        # Connect to SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
            print("Welcome email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")