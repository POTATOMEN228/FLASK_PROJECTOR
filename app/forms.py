from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from wtforms import TextAreaField, FileField
from flask_wtf.file import FileAllowed
from wtforms import SelectField, TextAreaField

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    about_me = TextAreaField('About me')
    profile_image = FileField('Profile photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Save changes')

from wtforms import SelectField, TextAreaField

class RecipeForm(FlaskForm):
    title = StringField('Name', validators=[DataRequired()])
    short_description = StringField('Краткое описание', validators=[DataRequired()])
    instructions = TextAreaField('Полный рецепт', validators=[DataRequired()])
    category = SelectField('Категория', choices=[
        ('Европейская', 'Европейская'),
        ('Тайская', 'Тайская'),
        ('Итальянская', 'Итальянская'),
        ('Мексиканская', 'Мексиканская'),
        ('Славянская', 'Славянская'),
        ('Другие', 'Другие')
    ])
    image = FileField('Фото рецепта', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Добавить рецепт')


