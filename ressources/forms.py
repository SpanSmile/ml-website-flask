from flask_wtf import FlaskForm
from flask import request
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, Optional, NumberRange
from ressources.models import User, Exercise

class CreateUserForm(FlaskForm):
    username = StringField('User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField('Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField('Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    authority = SelectField('Authority:', choices=[('0', 'Admin'), ('1', 'Teacher'), ('2', 'Student')], validators=[DataRequired()])
    create = SubmitField('Create User')

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different username')

    def validate_email(self, email_to_check):
        email = User.query.filter_by(email_address=email_to_check.data).first()
        if email:
            raise ValidationError('Email address already exists. Please choose a different email address')

class EditUserForm(FlaskForm):
    username = StringField('User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField('Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField('Password:', validators=[Optional(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[Optional(), EqualTo('password1')])
    authority = SelectField('Authority:', choices=[('0', 'Admin'), ('1', 'Teacher'), ('2', 'Student')], validators=[DataRequired()])
    edit = SubmitField('Update User')

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super(EditUserForm, self).__init__(*args, **kwargs)

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user and user.id != self.current_user.id:
            raise ValidationError('Username already exists. Please choose a different username')

    def validate_email(self, email_to_check):
        email = User.query.filter_by(email_address=email_to_check.data).first()
        if email and email.id != self.current_user.id:
            raise ValidationError('Email address already exists. Please choose a different email address')

    
class LoginForm(FlaskForm):
    username = StringField('User Name:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class ExerciseForm(FlaskForm):
    def validate_exercise_name(self, name_to_check):
        exercise = Exercise.query.filter_by(name=name_to_check.data).first()
        if exercise:
            # Check if we're editing an existing exercise
            if request.view_args and 'id' in request.view_args:
                # If the exercise with this name is not the one we're editing, raise an error
                if exercise.id != request.view_args['id']:
                    raise ValidationError('Exercise name already exists. Please choose another name')
            else:
                # If we're creating a new exercise, raise an error
                raise ValidationError('Exercise name already exists. Please choose another name')
    
    exercise_name = StringField('Exercise name:', validators=[Length(min=2, max=30), DataRequired()])
    subject = StringField('Subject:', validators=[Length(min=2, max=60), DataRequired()])
    description = StringField('Description:', validators=[Length(min=2, max=1024), DataRequired()])
    content = TextAreaField('Content', validators=[Length(min=2), DataRequired()])
    create = SubmitField('Create Exercise')
    edit = SubmitField('Update Exercise')
    
class ContactUs(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class SubmitJobForm(FlaskForm):
    name = StringField("Job Name:", validators=[DataRequired(), Length(min=2, max=20)])
    folder_name = StringField("Folder Name:", validators=[DataRequired(), Length(min=2, max=20)])
    gpu_memory = IntegerField("GPU Memory (GB):", validators=[DataRequired(), NumberRange(min=1, max=24)])
    image_url = StringField("Image:", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Submit Job")
