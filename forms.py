from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    #author = StringField("Author",validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(),URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegistrationForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired()])
    password = StringField("Password",validators=[DataRequired()])
    name = StringField("Name",validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CommentForm(FlaskForm):
    comment = CKEditorField("Comment")
    submit = SubmitField("Submit comment")