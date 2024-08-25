import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///task_management.db'  # or use PostgreSQL/MySQL URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'  # change this to a random secret key
