from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User

class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # User profile data
    weight = FloatField('Weight (kg)', validators=[DataRequired()])
    height = FloatField('Height (cm)', validators=[DataRequired()])
    age = FloatField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', 
                        choices=[('', 'Select...'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                        validators=[DataRequired()])
    activity_level = SelectField('Activity Level', 
                              choices=[('', 'Select...'),
                                      ('sedentary', 'Sedentary (little or no exercise)'),
                                      ('light', 'Lightly active (light exercise 1-3 days/week)'),
                                      ('moderate', 'Moderately active (moderate exercise 3-5 days/week)'),
                                      ('active', 'Active (hard exercise 6-7 days/week)'),
                                      ('very_active', 'Very active (very hard exercise & physical job)')],
                              validators=[DataRequired()])
    motive = SelectField('Goal', 
                        choices=[('', 'Select...'),
                                ('lose', 'Lose weight'),
                                ('maintain', 'Maintain weight'),
                                ('gain', 'Gain weight')],
                        validators=[DataRequired()])
    
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class NaturalLanguageInputForm_Food(FlaskForm):
    query = TextAreaField('What did you eat?', validators=[DataRequired()])
    submit = SubmitField('Process')

class NaturalLanguageInputForm_Exercise(FlaskForm):
    query = TextAreaField('what exercise did you do?', validators=[DataRequired()])
    submit = SubmitField('Process')

class CustomItemForm(FlaskForm):
    name = StringField('Food Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    unit = SelectField('Unit',
        choices=[
            ('g', 'Grams (g)'),
            ('ml', 'Milliliters (ml)'),
            ('unit', 'Units (unit)')],
        validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    calories = FloatField('Calories', validators=[DataRequired()])
    protein = FloatField('Protein (g)', validators=[DataRequired()])
    carbohydrates = FloatField('Carbohydrates (g)', validators=[DataRequired()])
    fiber = FloatField('Fiber (g)', validators=[DataRequired()])
    sugar = FloatField('Sugar (g)', validators=[DataRequired()])
    sodium = FloatField('Sodium (mg)', validators=[DataRequired()])
    submit = SubmitField('Save Food Item')

class MealForm(FlaskForm):
    name = StringField('Meal Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Meal')

class MealItemForm(FlaskForm):
    custom_item_id = SelectField('Food Item', coerce=int, validators=[DataRequired()],  render_kw={"class": "form-control"})
    quantity = FloatField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add to Meal')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    weight = FloatField('Weight (kg)', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional()])
    age = FloatField('Age', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select...'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[Optional()])
    activity_level = SelectField('Activity Level', 
                              choices=[('', 'Select...'),
                                      ('sedentary', 'Sedentary (little or no exercise)'),
                                      ('light', 'Lightly active (light exercise 1-3 days/week)'),
                                      ('moderate', 'Moderately active (moderate exercise 3-5 days/week)'),
                                      ('active', 'Active (hard exercise 6-7 days/week)'),
                                      ('very_active', 'Very active (very hard exercise & physical job)')],
                              validators=[Optional()])
    motive = SelectField('Goal', 
                        choices=[('', 'Select...'),
                                ('lose', 'Lose weight'),
                                ('maintain', 'Maintain weight'),
                                ('gain', 'Gain weight')],
                        validators=[Optional()])
    submit = SubmitField('Update Profile')
