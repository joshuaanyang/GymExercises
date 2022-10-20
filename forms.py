from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


##WTForm
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("I'm ready to put the work in!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Take Me in!")


# might add a contact form
class ContactForm(FlaskForm):
    name = StringField("Name")
    email = StringField("Email Address")
    phone = StringField("Phone Number")
    message = StringField("Message")
    submit = SubmitField("Send")
