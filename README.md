# 🎓 Personal Academic Assistant

A full-stack web application that helps students manage their academics by tracking attendance, calculating GPA, predicting future GPA using Machine Learning, and generating academic reports.

---

## 📌 Features

### 👤 User Authentication
- Student Registration
- Secure Login & Logout
- Password Hashing
- Session Management

### 👤 Student Profile
- Store academic details
- Personal information management

### 📅 Attendance Tracker
- Add subject-wise attendance
- Automatic attendance percentage calculation
- Overall attendance analytics
- Delete attendance records

### 🎓 GPA Calculator
- Credit-based GPA calculation
- Grade to Grade Point conversion
- GPA analytics
- Delete GPA records

### 🧠 Machine Learning GPA Predictor
Predicts a student's future GPA using a trained Regression model based on:

- Age
- Gender
- Study Time
- Absences
- Tutoring
- Parental Support
- Extracurricular Activities
- Sports
- Music
- Volunteering

### 💡 Study Recommendations
Personalized recommendations are generated based on the predicted GPA.

### 📊 Dashboard
- Attendance Overview
- Current GPA
- Latest GPA Prediction
- Academic Health Score
- Attendance Chart
- GPA Chart

### 📄 PDF Report Generation
Generate downloadable academic reports containing:
- Attendance Summary
- GPA Summary
- Predicted GPA

---

# 🛠 Tech Stack

## Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Chart.js

## Backend
- Flask
- SQLAlchemy
- Flask-Login

## Database
- MySQL

## Machine Learning
- Scikit-learn
- NumPy
- Pandas
- Joblib

---

# 🤖 Machine Learning Model

Model Type:
Regression

The model predicts GPA using student academic and extracurricular information.

Dataset:
Student Performance Dataset (Kaggle)

---

# 📂 Project Structure

```
PersonalAcademicAssistant
│
├── app.py
├── config.py
├── models.py
├── requirements.txt
│
├── models/
│   └── gpa_regression_model.pkl
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── layout.html
│   ├── dashboard.html
│   ├── attendance.html
│   ├── gpa.html
│   ├── predict.html
│   ├── profile.html
│   ├── login.html
│   ├── signup.html
│   └── index.html
│
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/PersonalAcademicAssistant.git
```

Go into the project

```bash
cd PersonalAcademicAssistant
```

Create virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

---

# 📸 Screenshots

(Add screenshots here after deployment)

- Home Page
- Dashboard
- Attendance
- GPA Calculator
- GPA Predictor
- Academic Report

---

# 🔮 Future Improvements

- Email Notifications
- Attendance Prediction
- GPA Trend Forecasting
- Multi-semester Analytics
- Admin Dashboard
- Mobile App

---

# 👩‍💻 Author

**Sharini**

Built as a Machine Learning + Full Stack Flask portfolio project.