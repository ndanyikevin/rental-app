from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    identifier = StringField(
        "Username or email",
        validators=[
            DataRequired(message="Enter your username or email."),
            Length(max=120)
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Enter your password.")
        ]
    )

    submit = SubmitField("Sign in")


    
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
)


class LoginForm(FlaskForm):
    identifier = StringField(
        "Username or email",
        validators=[
            DataRequired(message="Enter your username or email."),
            Length(max=120),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Enter your password."),
        ],
    )

    submit = SubmitField("Sign in")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current password",
        validators=[DataRequired()],
    )

    new_password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            Length(
                min=12,
                message="Password must contain at least 12 characters.",
            ),
        ],
    )

    confirm_new_password = PasswordField(
        "Confirm new password",
        validators=[
            DataRequired(),
            EqualTo(
                "new_password",
                message="The new passwords do not match.",
            ),
        ],
    )

    submit = SubmitField("Change password")
