from flask_login import UserMixin, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField,FileRequired
from flask_wtf import FlaskForm
from wtforms import Form, StringField,BooleanField,TextAreaField,validators,SubmitField,DecimalField,PasswordField
from wtforms.validators import DataRequired,EqualTo,ValidationError,Email,Length


from .models import Register


class CustomerRegistrationForm(FlaskForm, UserMixin):
    name=StringField('Name:')
    username=StringField('Username:',validators=[DataRequired()])
    email=StringField('Email :',validators=[Email(),DataRequired()])
    password=PasswordField('Password:',validators=[DataRequired()])
    confirm=PasswordField('Confirm Password:',validators=[DataRequired(),EqualTo('password')])
    country=StringField('Country',validators=[DataRequired()])
    state=StringField('state',validators=[DataRequired()])
    city=StringField('city',validators=[DataRequired()])
    address=StringField('address',validators=[DataRequired()])
    contact=StringField('contact',validators=[DataRequired()])
    zipcode=StringField('zipcode',validators=[DataRequired()])

    profile=FileField('Profile',validators=[FileAllowed(['jpg','jpeg','png','jfif','gif'])])
    submit=SubmitField('Register')

    
    def validate_username(self,username):
        
        if Register.query.filter_by(username=username.data).first():
            print(username.data)
            raise ValidationError('Username already Exists')

    def validate_email(self,email):
        if Register.query.filter_by(email=email.data).first():
       
            raise ValidationError('Email already Exists')

class Customerloginform(FlaskForm):
    email=StringField('Email :',validators=[Email(),DataRequired()])
    password=PasswordField('Password:',validators=[DataRequired()])
    submit=SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    profile=FileField('Profile Pic',validators=[FileAllowed(['jpg','png','jpeg','jfif'])])
   
    submit = SubmitField('Update Profile')

    def validate_username(self,username):
        if username.data!= current_user:

            user=Register.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already Exists')

    def validate_email(self,email):
        if email.data != current_user.email:
            user=Register.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already Exists')