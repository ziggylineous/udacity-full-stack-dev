from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField
from wtforms import TextAreaField, SelectField
from wtforms.validators import DataRequired
from app.models import Category
from app import images


class LoginForm(FlaskForm):
    username = StringField('Your Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int)
    image = FileField('Item Image', validators=[
        FileAllowed(images, 'You can upload images only.')
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.category_id.choices = [
            (cat.id, cat.name) for cat in Category.query.order_by('name')
        ]
