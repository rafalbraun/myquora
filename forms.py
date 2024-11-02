from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, SelectField, FieldList, FormField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from models import Post, User

class CreatePostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('create')

class UpdatePostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('update')

class DeletePostForm(FlaskForm):
    content = TextAreaField('Content', validators=[])
    submit = SubmitField('confirm')

class CreateCommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    rid = IntegerField('', validators=[DataRequired()])
    pid = IntegerField('', validators=[DataRequired()])
    submit = SubmitField('create')
