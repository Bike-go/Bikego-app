from datetime import timedelta
import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_schema = os.getenv("POSTGRES_SCHEMA")

encoded_password = quote(postgres_password) if postgres_password else ""

SQLALCHEMY_DATABASE_URI = f"postgresql://{postgres_user}:{encoded_password}@{postgres_host}:{postgres_port}/{postgres_db}"

class Config:
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = os.getenv("FLASK_PORT", 5000)
    POSTGRES_SCHEMA = postgres_schema
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    URL_IN_EMAIL = os.getenv("URL_IN_EMAIL")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    JWT_COOKIE_SECURE = False
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True
    WTF_CSRF_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    WTF_CSRF_ENABLED = True
    CSRF_COOKIE_NAME = 'csrf_access_token'
    CSRF_SESSION_KEY = 'csrf_access_token'
    JWT_ACCESS_CSRF_FIELD_NAME = 'csrf_token'
    JWT_CSRF_CHECK_FORM = True
