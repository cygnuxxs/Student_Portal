from flask import Flask, render_template, url_for, redirect, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *

def admin_only(f):
    @wraps(f)
    def df(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return df

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "Cygnuxxs"
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(150), nullable = False)

class Student(db.Model):
    __tablename__ = "students"
    student_unique_id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.String(10), unique = True, nullable = False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    section = db.Column(db.String(6), nullable = False)

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.String(10), nullable = False)
    date = db.Column(db.Date, nullable =False)
    status = db.Column(db.String(7), nullable = False)
    section = db.Column(db.String(6), nullable = False)
    __table_args__ = (db.UniqueConstraint('student_id', "date", name = "unique_student_date"),)

class TimeTable(db.Model):
    __tablename__ = "timetable"
    id = db.Column(db.Integer, primary_key = True)
    day = db.Column(db.String(10), nullable = False)
    hour = db.Column(db.Integer, nullable = False)
    subject = db.Column(db.String(50), nullable = False)
    staff = db.Column(db.String(50), nullable = False)
    section = db.Column(db.String(6), nullable = False)
    __table_args__ = (db.UniqueConstraint("day", "hour", "section", name = "unique_entry"),)

with app.app_context() as con:
    db.create_all()

@app.route('/', methods = ['GET','POST'])
def home():
    form = GetStudentForm()
    error = None
    if form.validate_on_submit():
        student_id = form.student_id.data
        student = Student.query.filter_by(student_id = student_id.upper()).first()
        if student:
            return redirect(url_for("get_details", roll_num = student.student_id))
        else:
            error = "The entered Student ID is not found."
        
    return render_template('index.html', title = "Get Student Details", form = form, err = error)

@app.route("/admin", methods = ["GET", "POST"])
def admin():
    form = AdminForm()
    err = None
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Admin.query.filter_by(username = username).first()
        print(user)
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("add_details"))
            else:
                err = "Password is incorrect."

    return render_template("admin.html", form = form, err = err)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/student/<roll_num>')
def get_details(roll_num):
    err = None
    hours = None
    student = Student.query.filter_by(student_id = roll_num).first()
    if student:
        hour1 = TimeTable.query.filter_by(section = student.section).filter_by(hour = 1).all()
        hour2 = TimeTable.query.filter_by(section = student.section).filter_by(hour = 2).all()
        hour3 = TimeTable.query.filter_by(section = student.section).filter_by(hour = 3).all()
        hour4 = TimeTable.query.filter_by(section = student.section).filter_by(hour = 4).all()
        if not (hour1 == [] or hour2 == [] or hour3 == [] or hour4 == []):
            hours = [hour1, hour2, hour3, hour4]
    else:
        err = "The given student ID is not found in the database."
    staff = TimeTable.query.filter_by(section = student.section).all()
    staff_dict = {}
    for i in staff:
        if i.subject not in staff_dict:
            staff_dict[i.subject] = i.staff
    return render_template("student_details.html", staff = staff_dict, err = err, student = student, hours = hours)

@app.route("/add-details", methods = ['GET', 'POST'])
@login_required
@admin_only
def add_details():
    form = AddDetailsForm()
    err = None
    if form.validate_on_submit():
        student_id = form.student_id.data.upper()
        print(type(student_id))
        student = Student.query.filter_by(student_id = student_id).first()
        if student is None:
            first_name = form.first_name.data
            last_name = form.last_name.data
            date_of_birth = form.dob.data
            section = form.section.data

            new_student = Student(
                student_id = student_id,
                first_name = first_name,
                last_name = last_name,
                date_of_birth = date_of_birth,
                section = section
            )
            db.session.add(new_student)
            db.session.commit()
            err = f"{student_id} Student Details added Successfully."
        else:
            err = "The entered student ID is already in the database."
    return render_template('add_details.html',title = "Add Student Details", form = form, logged_in = current_user.is_authenticated, err = err)

@app.route("/sections", methods = ["GET", "POST"])
def section():
    err = None
    data = None
    aform = None
    form = SectionForm()
    if form.validate_on_submit():
        section = form.sections.data
        data = Student.query.filter_by(section = section).order_by(Student.student_id).all()
        for student in data:
            setattr(AttendanceForm, f"{student.student_id}", BooleanField("Present"))
        aform = AttendanceForm()
        if aform.validate_on_submit():
            for field in aform:
                if field.name != "submit" and field.name != "csrf_token" and field.name != "confirm":
                    new_entry = Attendance(
                        student_id = field.name,
                        date = form.date.data,
                        status = "Present" if field.data else "Absent",
                        section = form.sections.data
                    )
                    try:
                        db.session.add(new_entry)
                        db.session.commit()
                        err = "Attendance Posted Successfully."
                    except IntegrityError:
                        db.session.rollback()
                        err = "Attendance already taken for this section."
    return render_template("sections.html", err = err, aform = aform, form = form, title = "Section wise Attendance", data = data)

@app.route("/add-staff", methods = ['GET', "POST"])
@login_required
@admin_only
def staff():
    form = StaffForm()
    err = None
    if form.validate_on_submit():
        day = form.day.data
        hour = form.hour.data
        subject = form.subject.data
        mentor = form.staff.data
        section = form.section.data
        new_entry = TimeTable(
            day = day,
            hour = hour,
            subject = subject,
            staff = mentor,
            section = section
        )
        try:
            db.session.add(new_entry)
            db.session.commit()
            err = "Entries are successfully Updated."
        except IntegrityError:
            db.session.rollback()
            err = "Entry is already in the database."
    return render_template("add-staff.html", form = form, err = err)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 