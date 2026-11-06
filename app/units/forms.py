
from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    StringField,
    IntegerField,
    DecimalField,
    TextAreaField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
)

from app.units.constants import UNIT_TYPE_CHOICES


class UnitForm(FlaskForm):
    """Form for registering and updating rental units."""

    # -------------------------------------------------------------
    # Property and unit identification
    # -------------------------------------------------------------

    property_id = SelectField(
        "Property",
        coerce=int,
        validators=[
            InputRequired(
                message="Select a property."
            ),
            NumberRange(
                min=1,
                message="Select a valid property.",
            ),
        ],
    )

    unit_number = StringField(
        "Unit number",
        validators=[
            DataRequired(
                message="Enter the unit number."
            ),
            Length(
                max=50,
                message="Unit number cannot exceed 50 characters.",
            ),
        ],
    )

    unit_type = SelectField(
        "Unit type",
        choices=UNIT_TYPE_CHOICES,
        validators=[
            DataRequired(
                message="Select a unit type."
            ),
        ],
    )

    custom_unit_type = StringField(
        "Specify unit type",
        validators=[
            Optional(),
            Length(
                max=50,
                message="Custom unit type cannot exceed 50 characters.",
            ),
        ],
    )

    # -------------------------------------------------------------
    # Unit specifications
    # -------------------------------------------------------------

    bedrooms = IntegerField(
        "Bedrooms",
        default=1,
        validators=[
            InputRequired(
                message="Enter the number of bedrooms."
            ),
            NumberRange(
                min=0,
                message="Bedrooms cannot be negative.",
            ),
        ],
    )

    bathrooms = IntegerField(
        "Bathrooms (inside unit)",
        default=0,
        validators=[
            InputRequired(
                message="Enter the number of bathrooms."
            ),
            NumberRange(
                min=0,
                message="Bathrooms cannot be negative.",
            ),
        ],
    )

    # -------------------------------------------------------------
    # Rental information
    # -------------------------------------------------------------

    default_rent = DecimalField(
        "Monthly rent (KES)",
        places=2,
        validators=[
            InputRequired(
                message="Enter the monthly rent."
            ),
            NumberRange(
                min=0,
                message="Rent cannot be negative.",
            ),
        ],
        render_kw={
            "step": "0.01",
            "min": "0",
            "placeholder": "0.00",
        },
    )

    status = SelectField(
        "Status",
        choices=[
            ("available", "Available"),
            ("maintenance", "Under maintenance"),
            ("occupied", "Occupied"),
        ],
        default="available",
        validators=[
            DataRequired(
                message="Select a unit status."
            ),
        ],
    )

    # -------------------------------------------------------------
    # Additional information
    # -------------------------------------------------------------

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField("Save unit")

    # -------------------------------------------------------------
    # Custom validation
    # -------------------------------------------------------------

    def validate_custom_unit_type(self, field):
        """Require a custom type when Other is selected."""

        if self.unit_type.data == "Other" and not field.data:
            raise ValueError(
                "Please specify the custom unit type."
            )
