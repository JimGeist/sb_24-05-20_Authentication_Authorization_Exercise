from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Regexp


class RegistrationForm(FlaskForm):
    """ Registration form for a new user. """

    username = StringField("Username", validators=[
        Length(min=4, max=20,
               message="REQUIRED, Username must be 4 to 20 characters in length.")])
    password = PasswordField("Password", validators=[
        Length(min=6, message="REQUIRED, Password must be at least 6 characters in length.")])
    email = StringField("Email", validators=[
        Email(message="REQUIRED, Email is not formatted correctly."),
        Length(min=1, max=50, message="REQUIRED, Email must be 1 to 50 characters in length.")])
    first_name = StringField("First Name", validators=[
        Length(min=1, max=30, message="REQUIRED, First Name must be 1 to 30 characters in length.")])
    last_name = StringField("Last Name", validators=[
        Length(min=1, max=30, message="REQUIRED, Last Name must be 1 to 30 characters in length.")])
    # last_name = StringField("Last Name", validators=[
    #     Regexp("/^\s$/", message="REQUIRED, Last Name cannot be spaces."),
    #     Length(min=1, max=30, message="REQUIRED, Last Name must be 1 to 30 characters in length.")])
    # last_name = StringField("Last Name", validators=[
    #     Regexp("/\s/", message="REQUIRED, Last Name cannot be spaces."),
    #     Length(min=1, max=30, message="REQUIRED, Last Name must be 1 to 30 characters in length.")])


class LoginForm(FlaskForm):
    """ Login Form for an existing user. """

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    """ Feedback Form for a user to add feedback. """

    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Feedback", validators=[InputRequired()])
