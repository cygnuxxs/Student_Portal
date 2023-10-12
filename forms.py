from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField, SubmitField, DateField, SelectField, BooleanField, FieldList, FormField, PasswordField

sections_list = [("K1CSD", "K1CSD"),
                 ("K1CSM", "K1CSM"),
                 ("K1CAI", "K1CAI"),
                 ("K1CSC", "K1CSC"),
                 ("K1AID", "K1AID"),
                 ("K2CSD", "K2CSD"),
                 ("K2CSM", "K2CSM"),
                 ("K2CAI", "K2CAI"),
                 ("K2CSC", "K2CSC"),
                 ("K2AID", "K2AID")]

staff_list = [
            ("Uday", "Uday"),
            ("Sowjanya", "Sowjanya"),
            ("Anitha", "Anitha"),
            ("Sushmitha", "Sushmitha"),
            ("Sujitha", "Sujitha"),
            ("Raju", "Raju"),
            ("Ramakrishna", "Ramakrishna"),
            ("Veeramani", "Veeramani"),
            ("Veeralakshmi", "Veeralakshmi"),
            ("Khan", "Khan"),
            ("Rohini", "Rohini"),
            ("Suresh", "Suresh"),
            ("Tirupathi Rao (LL)", "Tirupathi Rao (LL)"),
            ("Ganesh (LL)", "Ganesh (LL)"),
            ("Mani Kumar (LL)", "Mani Kumar (LL)"),
            ("Others", "Others")
]

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
hours = [1,2,3,4]

class GetStudentForm(FlaskForm):
    student_id = StringField("Student Roll Number", [DataRequired(), Length(min=10, max=10)])
    get_details = SubmitField("Get Details")

class AdminForm(FlaskForm):
    username = StringField("Username", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Submit")

class AddDetailsForm(FlaskForm):
    student_id = StringField("Student Roll Number", [DataRequired(), Length(min=10, max=10)])
    first_name = StringField("First Name", [DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", [DataRequired(), Length(max=50)])
    dob = DateField("Date of Birth", format = "%d-%m-%Y", validators=[DataRequired()], render_kw = {"type":"text"})
    section = SelectField("Section", validators=[DataRequired()], choices=sections_list)
    add_details = SubmitField("Add Details")

class SectionForm(FlaskForm):
    sections = SelectField("Sections", choices=sections_list, validators=[DataRequired()])
    submit = SubmitField("Submit")

class StaffForm(FlaskForm):
    day = SelectField("Day", choices=days, validators=[DataRequired()])
    hour = SelectField("Hour", choices=hours, validators=[DataRequired()])
    subject = StringField("Subject Name", [DataRequired()])
    staff = SelectField("Faculty Name", validators=[DataRequired()], choices=staff_list)
    section = SelectField("Section", choices=sections_list, validators=[DataRequired()])
    submit = SubmitField("Submit")
    


