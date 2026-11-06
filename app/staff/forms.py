
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
)


class StaffForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
        ],
    )

    email = StringField(
        "Email address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120),
        ],
    )

    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[DataRequired()],
    )

    submit = SubmitField("Save staff member")


class CreateStaffForm(StaffForm):
    password = PasswordField(
        "Initial password",
        validators=[
            DataRequired(),
            Length(min=12, message="Password must contain at least 12 characters."),
        ],
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords do not match."),
        ],
    )

    submit = SubmitField("Create staff member")


class ResetStaffPasswordForm(FlaskForm):
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            Length(min=12, message="Password must contain at least 12 characters."),
        ],
    )

    confirm_password = PasswordField(
        "Confirm new password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords do not match."),
        ],
    )

    submit = SubmitField("Reset password")
