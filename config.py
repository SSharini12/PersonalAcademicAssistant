import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "academicassistant123")

    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root123@localhost/academic_assistant"
    )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg2://",
            1
        )

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False