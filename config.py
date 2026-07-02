import os

class Config:
    SECRET_KEY = "academicassistant123"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root123@localhost/academic_assistant"

    SQLALCHEMY_TRACK_MODIFICATIONS = False