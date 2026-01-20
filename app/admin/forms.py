from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, PasswordField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Optional

from ..models import Rank

class LoginForm(FlaskForm):
    username = StringField("Username (Last name)", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class UserForm(FlaskForm):
    rank = SelectField("Rank", choices=[(r.value, r.value) for r in Rank], validators=[DataRequired()])
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    internal_phone = StringField("Internal phone", validators=[Optional()])
    mobile_phone = StringField("Mobile phone", validators=[Optional()])
    active = BooleanField("Active")
    is_admin = BooleanField("Admin")
    password = PasswordField("Admin password (set/replace)", validators=[Optional()])


class ProjectForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    status = SelectField("Status", choices=[("active", "active"), ("archived", "archived")], validators=[DataRequired()])


class TaskForm(FlaskForm):
    project_id = SelectField("Project", coerce=int, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    assign_date = DateField("Assign date", default=date.today, validators=[Optional()])
    deadline = DateField("Deadline", validators=[Optional()])
    delivery_date = DateField("Delivery date", validators=[Optional()])
    status = SelectField("Status", choices=[
        ("in_progress", "In Progress"),
        ("backlog", "Backlog"),
        ("blocked", "Blocked"),
        ("done", "Done"),
    ], validators=[DataRequired()])
    priority = SelectField("Priority", choices=[
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ], validators=[DataRequired()])
    assignees = SelectMultipleField("Assignees", coerce=int, validators=[DataRequired()])


class AttachmentForm(FlaskForm):
    label = StringField("Label", validators=[DataRequired()])
    path = StringField("Path/URL", validators=[DataRequired()])


class CommentForm(FlaskForm):
    body = TextAreaField("Comment", validators=[DataRequired()])
