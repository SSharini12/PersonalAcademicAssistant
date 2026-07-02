import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "academicassistant123")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:root123@localhost/academic_assistant"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False