from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    

class UserEditForm(FlaskForm):
    """Form for editing users"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class WishlistForm(FlaskForm):
    """Form for creating a wish list"""
    name = StringField('Name', validators=[DataRequired()] )

class SearchItemForm(FlaskForm):
    """Form for searching for items"""
    name = StringField('Name', validators=[DataRequired()])

class AddItemForm(FlaskForm):
    """Form for adding Items to wishlist"""
    name = StringField('Description')
    url = HiddenField('Image url')
