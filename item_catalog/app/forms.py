from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.models import Category

class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.category_id.choices = [
            (cat.id, cat.name) for cat in Category.query.order_by('name')
        ]
