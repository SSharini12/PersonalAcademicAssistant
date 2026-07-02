from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
import tempfile
import os
import joblib
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, Student, Attendance, GPA, Prediction
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object(Config)

BASE = os.path.dirname(os.path.abspath(__file__))

gpa_model = joblib.load(
    os.path.join(BASE, "models", "gpa_regression_model.pkl")
)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Student, int(user_id))


with app.app_context():
    db.create_all()


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- SIGNUP ---------------- #

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        department = request.form["department"]
        semester = request.form["semester"]

        existing = Student.query.filter_by(email=email).first()

        if existing:
            flash("Email already registered!")
            return redirect(url_for("signup"))

        student = Student(
            name=name,
            email=email,
            password=password,
            department=department,
            semester=semester
        )

        db.session.add(student)
        db.session.commit()

        flash("Registration Successful!")
        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = Student.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully!")

    return redirect(url_for("home"))


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
@login_required
def dashboard():

    attendance_records = Attendance.query.filter_by(
        student_id=current_user.student_id
    ).all()

    gpa_records = GPA.query.filter_by(
        student_id=current_user.student_id
    ).all()

    attendance = 0

    if attendance_records:

        attendance = round(
            sum(r.attendance_percentage for r in attendance_records)
            / len(attendance_records),
            2
        )

    total_points = 0
    total_credits = 0

    for row in gpa_records:

        total_points += row.grade_points * row.credits
        total_credits += row.credits

    current_gpa = 0

    if total_credits:

        current_gpa = round(
            total_points / total_credits,
            2
        )

    total_subjects = len(gpa_records)

    attendance_subjects = [
        r.subject for r in attendance_records
    ]

    attendance_values = [
        r.attendance_percentage for r in attendance_records
    ]

    gpa_subjects = [
        r.subject for r in gpa_records
    ]

    gpa_values = [
        r.grade_points for r in gpa_records
    ]

    latest_prediction = Prediction.query.filter_by(
        student_id=current_user.student_id
    ).order_by(
        Prediction.prediction_date.desc()
    ).first()

    # ---------------- Academic Health Score ---------------- #

    prediction_score = 0

    if latest_prediction:
        prediction_score = latest_prediction.predicted_gpa * 10

    health_score = round(

        (attendance * 0.4)

        + (current_gpa * 10 * 0.4)

        + (prediction_score * 0.2)

    )

    health_score = max(0, min(100, health_score))
    # Academic Status

    if health_score >= 85:
        health_status = "Excellent"
        health_color = "success"

    elif health_score >= 70:
        health_status = "Good"
        health_color = "warning"

    else:
        health_status = "Needs Improvement"
        health_color = "danger"
    return render_template(
        "dashboard.html",
        student=current_user,
        overall_attendance=attendance,
        current_gpa=current_gpa,
        total_subjects=total_subjects,
        attendance_subjects=attendance_subjects,
        attendance_values=attendance_values,
        gpa_subjects=gpa_subjects,
        gpa_values=gpa_values,
        latest_prediction=latest_prediction,
        health_score=health_score,
        health_status=health_status,
        health_color=health_color
    )
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        current_user.age = int(request.form["age"])
        current_user.gender = int(request.form["gender"])
        current_user.study_time = float(request.form["study_time"])
        current_user.absences = int(request.form["absences"])
        current_user.tutoring = int(request.form["tutoring"])
        current_user.parental_support = int(request.form["parental_support"])
        current_user.extracurricular = int(request.form["extracurricular"])
        current_user.sports = int(request.form["sports"])
        current_user.music = int(request.form["music"])
        current_user.volunteering = int(request.form["volunteering"])

        db.session.commit()

        flash("Profile Updated Successfully!")

        return redirect(url_for("profile"))

    return render_template(
        "profile.html",
        student=current_user
    )


# ---------------- ATTENDANCE ---------------- #

@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():

    if request.method == "POST":

        subject = request.form["subject"]

        attended = int(request.form["attended"])

        total = int(request.form["total"])

        if total <= 0:

            flash("Total classes must be greater than 0.")

            return redirect(url_for("attendance"))

        if attended > total:

            flash("Attended classes cannot exceed total classes.")

            return redirect(url_for("attendance"))

        percentage = round((attended / total) * 100, 2)

        record = Attendance(
            student_id=current_user.student_id,
            subject=subject,
            classes_attended=attended,
            total_classes=total,
            attendance_percentage=percentage
        )

        db.session.add(record)
        db.session.commit()

        flash("Attendance Added Successfully!")

        return redirect(url_for("attendance"))

    records = Attendance.query.filter_by(
        student_id=current_user.student_id
    ).all()

    overall = 0

    if records:

        overall = round(
            sum(r.attendance_percentage for r in records) / len(records),
            2
        )

    return render_template(
        "attendance.html",
        records=records,
        overall=overall
    )


# ---------------- DELETE ATTENDANCE ---------------- #

@app.route("/attendance/delete/<int:id>")
@login_required
def delete_attendance(id):

    record = Attendance.query.get_or_404(id)

    if record.student_id != current_user.student_id:

        flash("Unauthorized Action!")

        return redirect(url_for("attendance"))

    db.session.delete(record)
    db.session.commit()

    flash("Attendance Deleted Successfully!")

    return redirect(url_for("attendance"))


# ---------------- GPA ---------------- #

@app.route("/gpa", methods=["GET", "POST"])
@login_required
def gpa():

    grade_map = {
        "O": 10,
        "A+": 9,
        "A": 8,
        "B+": 7,
        "B": 6,
        "C": 5,
        "F": 0
    }

    if request.method == "POST":

        subject = request.form["subject"]
        credits = int(request.form["credits"])
        grade = request.form["grade"]

        points = grade_map[grade]

        record = GPA(
            student_id=current_user.student_id,
            subject=subject,
            credits=credits,
            grade=grade,
            grade_points=points
        )

        db.session.add(record)
        db.session.commit()

        flash("Subject Added Successfully!")

        return redirect(url_for("gpa"))

    records = GPA.query.filter_by(
        student_id=current_user.student_id
    ).all()

    total_points = 0
    total_credits = 0

    for row in records:
        total_points += row.credits * row.grade_points
        total_credits += row.credits

    gpa_value = 0

    if total_credits > 0:
        gpa_value = round(total_points / total_credits, 2)

    return render_template(
        "gpa.html",
        records=records,
        gpa=gpa_value
    )

@app.route("/gpa/delete/<int:id>")
@login_required
def delete_gpa(id):

    record = GPA.query.get_or_404(id)

    if record.student_id != current_user.student_id:
        flash("Unauthorized Action!")
        return redirect(url_for("gpa"))

    db.session.delete(record)
    db.session.commit()

    flash("Subject Deleted Successfully!")

    return redirect(url_for("gpa"))


# ---------------- PREDICT ---------------- #

@app.route("/predict", methods=["GET", "POST"])
@login_required
def predictor():

    predicted_gpa = None
    recommendation = None

    if request.method == "POST":

        age = int(request.form["age"])
        gender = int(request.form["gender"])
        study_time = float(request.form["study_time"])
        absences = int(request.form["absences"])
        tutoring = int(request.form["tutoring"])
        parental_support = int(request.form["parental_support"])
        extracurricular = int(request.form["extracurricular"])
        sports = int(request.form["sports"])
        music = int(request.form["music"])
        volunteering = int(request.form["volunteering"])

        # Prepare input for ML model
        features = np.array([[
            age,
            gender,
            study_time,
            absences,
            tutoring,
            parental_support,
            extracurricular,
            sports,
            music,
            volunteering
        ]])

        # Predict GPA
        prediction = gpa_model.predict(features)
        predicted_gpa = round(float(prediction[0]), 2)

        # Save prediction to database
        prediction_record = Prediction(
            student_id=current_user.student_id,
            predicted_gpa=predicted_gpa
        )

        db.session.add(prediction_record)
        db.session.commit()

        # Generate study recommendations
        if predicted_gpa >= 8.5:

            recommendation = [
                "Excellent academic performance!",
                "Maintain your current study routine.",
                "Keep attending classes regularly.",
                "Continue participating in extracurricular activities."
            ]

        elif predicted_gpa >= 7:

            recommendation = [
                "Good academic performance.",
                "Increase study time slightly.",
                "Reduce unnecessary absences.",
                "Practice previous year question papers."
            ]

        else:

            recommendation = [
                "Performance needs improvement.",
                "Increase study hours every week.",
                "Attend tutoring sessions regularly.",
                "Reduce absences as much as possible.",
                "Focus more on difficult subjects."
            ]

    return render_template(
        "predict.html",
        predicted_gpa=predicted_gpa,
        recommendation=recommendation
    )
# ---------------- RECOMMENDATIONS ---------------- #

@app.route("/recommendation")
@login_required
def recommendation():

    # Attendance
    attendance_records = Attendance.query.filter_by(
        student_id=current_user.student_id
    ).all()

    overall_attendance = 0

    if attendance_records:
        overall_attendance = round(
            sum(r.attendance_percentage for r in attendance_records)
            / len(attendance_records),
            2
        )

    # GPA
    gpa_records = GPA.query.filter_by(
        student_id=current_user.student_id
    ).all()

    total_points = 0
    total_credits = 0

    for row in gpa_records:
        total_points += row.grade_points * row.credits
        total_credits += row.credits

    current_gpa = 0

    if total_credits:
        current_gpa = round(total_points / total_credits, 2)

    # Latest Prediction
    latest_prediction = Prediction.query.filter_by(
        student_id=current_user.student_id
    ).order_by(
        Prediction.prediction_date.desc()
    ).first()

    recommendations = []

    # ---------------- Attendance ----------------

    if overall_attendance >= 90:
        recommendations.append(
            "🎉 Excellent attendance! Keep maintaining your consistency."
        )
    elif overall_attendance >= 75:
        recommendations.append(
            "👍 Your attendance is good, but don't miss too many classes."
        )
    else:
        recommendations.append(
            "⚠️ Your attendance is below 75%. Attend every upcoming class."
        )

    # ---------------- GPA ----------------

    if current_gpa >= 9:
        recommendations.append(
            "🏆 Outstanding GPA! Keep challenging yourself."
        )
    elif current_gpa >= 8:
        recommendations.append(
            "📚 You're doing well. A little extra revision can push you above 9."
        )
    elif current_gpa >= 7:
        recommendations.append(
            "📖 Increase study hours and revise weekly."
        )
    else:
        recommendations.append(
            "🚨 Your GPA needs improvement. Focus on your weakest subjects."
        )

    # ---------------- Prediction ----------------

    if latest_prediction:

        if latest_prediction.predicted_gpa >= 9:
            recommendations.append(
                "🌟 Your predicted GPA is excellent. Maintain your routine."
            )

        elif latest_prediction.predicted_gpa >= 8:
            recommendations.append(
                "💡 You're on track for a strong GPA. Stay consistent."
            )

        else:
            recommendations.append(
                "📈 Your predicted GPA can improve. Increase study time and reduce absences."
            )

    # ---------------- Profile ----------------

    if current_user.study_time is not None:

        if current_user.study_time < 2:
            recommendations.append(
                "⏰ Try studying at least 2–3 hours daily."
            )

    if current_user.absences is not None:

        if current_user.absences > 10:
            recommendations.append(
                "📅 High absences detected. Regular attendance will improve performance."
            )

    if current_user.tutoring == 0:
        recommendations.append(
            "👨‍🏫 Consider joining tutoring sessions for difficult subjects."
        )

    if current_user.extracurricular == 0:
        recommendations.append(
            "🎭 Participating in extracurricular activities can improve overall development."
        )

    return render_template(
        "recommendation.html",
        recommendations=recommendations,
        attendance=overall_attendance,
        current_gpa=current_gpa,
        latest_prediction=latest_prediction
    )
# ---------------- ANALYTICS ---------------- #

@app.route("/analytics")
@login_required
def analytics():

    attendance_records = Attendance.query.filter_by(
        student_id=current_user.student_id
    ).all()

    gpa_records = GPA.query.filter_by(
        student_id=current_user.student_id
    ).all()

    attendance_subjects = [r.subject for r in attendance_records]
    attendance_values = [r.attendance_percentage for r in attendance_records]

    gpa_subjects = [r.subject for r in gpa_records]
    gpa_values = [r.grade_points for r in gpa_records]

    avg_attendance = 0
    if attendance_values:
        avg_attendance = round(sum(attendance_values) / len(attendance_values), 2)

    avg_gpa = 0
    if gpa_values:
        avg_gpa = round(sum(gpa_values) / len(gpa_values), 2)

    return render_template(
        "analytics.html",
        attendance_subjects=attendance_subjects,
        attendance_values=attendance_values,
        gpa_subjects=gpa_subjects,
        gpa_values=gpa_values,
        avg_attendance=avg_attendance,
        avg_gpa=avg_gpa
    )

# ---------------- DOWNLOAD PDF REPORT ---------------- #

@app.route("/download-report")
@login_required
def download_report():

    attendance_records = Attendance.query.filter_by(
        student_id=current_user.student_id
    ).all()

    gpa_records = GPA.query.filter_by(
        student_id=current_user.student_id
    ).all()

    latest_prediction = Prediction.query.filter_by(
        student_id=current_user.student_id
    ).order_by(
        Prediction.prediction_date.desc()
    ).first()

    # ---------------- Attendance ---------------- #

    overall_attendance = 0

    if attendance_records:

        overall_attendance = round(
            sum(r.attendance_percentage for r in attendance_records)
            / len(attendance_records),
            2
        )

    # ---------------- GPA ---------------- #

    total_points = 0
    total_credits = 0

    for row in gpa_records:

        total_points += row.grade_points * row.credits
        total_credits += row.credits

    current_gpa = 0

    if total_credits:

        current_gpa = round(
            total_points / total_credits,
            2
        )

    # ---------------- Recommendations ---------------- #

    recommendations = []

    if overall_attendance < 75:
        recommendations.append(
            "Improve your attendance."
        )
    else:
        recommendations.append(
            "Excellent attendance."
        )

    if current_gpa < 7:
        recommendations.append(
            "Increase study hours."
        )
    elif current_gpa < 8.5:
        recommendations.append(
            "Practice previous year papers."
        )
    else:
        recommendations.append(
            "Maintain your current performance."
        )

    # ---------------- PDF ---------------- #

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    doc = SimpleDocTemplate(temp.name)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>PERSONAL ACADEMIC REPORT</b>", styles["Title"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Name:</b> {current_user.name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Email:</b> {current_user.email}", styles["Normal"]))
    story.append(Paragraph(f"<b>Department:</b> {current_user.department}", styles["Normal"]))
    story.append(Paragraph(f"<b>Semester:</b> {current_user.semester}", styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(
        f"<b>Overall Attendance:</b> {overall_attendance}%",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"<b>Current GPA:</b> {current_gpa}",
        styles["Normal"]
    ))

    if latest_prediction:

        story.append(Paragraph(
            f"<b>Predicted GPA:</b> {latest_prediction.predicted_gpa}",
            styles["Normal"]
        ))

    else:

        story.append(Paragraph(
            "<b>Predicted GPA:</b> Not Available",
            styles["Normal"]
        ))

    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))

    for item in recommendations:

        story.append(
            Paragraph(f"• {item}", styles["Normal"])
        )

    doc.build(story)

    return send_file(
        temp.name,
        as_attachment=True,
        download_name="Academic_Report.pdf"
    )
if __name__ == "__main__":
    app.run(debug=True)