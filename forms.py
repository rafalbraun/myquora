from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, SelectField, FieldList, FormField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, URL
from models import Post, User

class CreatePostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField('create')

class UpdatePostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=10000)])
    submit = SubmitField('update')

class DeletePostForm(FlaskForm):
    content = TextAreaField('Content', validators=[])
    submit = SubmitField('confirm')

class CreateCommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[Optional(), Length(max=10000)])
    rid = IntegerField('', validators=[DataRequired()])
    pid = IntegerField('', validators=[DataRequired()])
    link = StringField('URL', validators=[URL(), Optional()])
    image_file = FileField('Upload File', validators=[Optional()])
    submit1 = SubmitField('create')

class ReportPostForm(FlaskForm):
    id = IntegerField('', validators=[])
    reason = RadioField('report reason', choices=[('v1','violence'),('v2','spam'),('v3','obscenity'),('v4','other')], validators=[DataRequired()])
    reported_post = IntegerField('', validators=[DataRequired()])
    submit2 = SubmitField('confirm')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=120)])
    submit = SubmitField('login')
