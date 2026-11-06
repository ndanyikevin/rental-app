
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
)


class PropertyForm(FlaskForm):
    name = StringField(
        "Property name",
        validators=[
            DataRequired(message="Enter the property name."),
            Length(max=120),
        ],
    )

    property_code = StringField(
        "Property code",
        validators=[
            DataRequired(message="Enter a property code."),
            Length(max=50),
        ],
    )

    address = StringField(
        "Physical address",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    town = StringField(
        "Town",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()],
    )

    submit = SubmitField("Save property")


class TogglePropertyStatusForm(FlaskForm):
    submit = SubmitField("Confirm")
