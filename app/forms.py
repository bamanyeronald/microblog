from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from sqlalchemy import select
from app import db

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(select(User.username).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please Enter a different Username')
        
    def validate_email(self, email):
        user = db.session.scalar(select(User.email).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please enter a different email address')
        
class EditProfileForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=200)])
    submit = SubmitField('submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(select(User).where(User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username')
            

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostFoam(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Submit')