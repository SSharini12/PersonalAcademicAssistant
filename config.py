import os

class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "academicassistant123"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///academic.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False