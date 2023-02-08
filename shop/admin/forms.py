from wtforms import Form, StringField, PasswordField, validators,SubmitField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms.validators import DataRequired,EqualTo,Length,Email

class RegistrationForm(Form):
    name = StringField('Name', validators=[DataRequired(),Length(min=4, max=25)])
    username = StringField('Username',validators= [DataRequired(),Length(min=4, max=25)])
    email = StringField('Email Address',validators= [DataRequired(),Length(min=6, max=35),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    profile=FileField('Profile',validators=[FileAllowed(['jpg','png','jpeg','jfif'])])


    submit = SubmitField('Sign Up')



class LoginForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
   
    submit = SubmitField('Login')
