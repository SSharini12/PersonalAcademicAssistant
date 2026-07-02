from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# ==========================
# Student Model
# ==========================
class Student(UserMixin, db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    department = db.Column(db.String(100))

    semester = db.Column(db.Integer)

    # ---------- ML Profile ----------

    age = db.Column(db.Integer)

    gender = db.Column(db.Integer)

    study_time = db.Column(db.Float)

    absences = db.Column(db.Integer)

    tutoring = db.Column(db.Integer)

    parental_support = db.Column(db.Integer)

    extracurricular = db.Column(db.Integer)

    sports = db.Column(db.Integer)

    music = db.Column(db.Integer)

    volunteering = db.Column(db.Integer)

    def get_id(self):
        return str(self.student_id)

# ==========================
# Attendance Model
# ==========================
class Attendance(db.Model):
    __tablename__ = "attendance"

    attendance_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id"),
        nullable=False
    )

    subject = db.Column(db.String(100), nullable=False)

    classes_attended = db.Column(db.Integer, nullable=False)

    total_classes = db.Column(db.Integer, nullable=False)

    attendance_percentage = db.Column(db.Float, nullable=False)

class GPA(db.Model):
    __tablename__ = "gpa"

    gpa_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id"),
        nullable=False
    )

    subject = db.Column(db.String(100), nullable=False)

    credits = db.Column(db.Integer, nullable=False)

    grade = db.Column(db.String(2), nullable=False)

    grade_points = db.Column(db.Float, nullable=False)

class Prediction(db.Model):
    __tablename__ = "predictions"

    prediction_id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id"),
        nullable=False
    )

    predicted_gpa = db.Column(
        db.Float,
        nullable=False
    )

    prediction_date = db.Column(
        db.DateTime,
        default=db.func.now()
    )