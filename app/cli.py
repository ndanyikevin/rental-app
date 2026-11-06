
import click
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Role, User


DEFAULT_ROLES = {
    "Administrator": {
        "description": "Full access to all RentalHub features.",
        "permissions": {"*": ["*"]},
    },
    "Manager": {
        "description": "Manages property operations and financial activities.",
        "permissions": {
            "dashboard": ["view"],
            "properties": ["view", "create", "edit", "delete"],
            "units": ["view", "create", "edit", "delete"],
            "tenants": ["view", "create", "edit", "delete"],
            "leases": ["view", "create", "edit", "delete"],
            "payments": ["view", "create", "edit"],
            "expenses": ["view", "create", "edit"],
            "maintenance": ["view", "create", "edit"],
            "reports": ["view", "export"],
        },
    },
    "Accountant": {
        "description": "Manages payments, expenses and financial reports.",
        "permissions": {
            "dashboard": ["view"],
            "payments": ["view", "create", "edit"],
            "expenses": ["view", "create", "edit"],
            "reports": ["view", "export"],
        },
    },
    "Caretaker": {
        "description": "Handles assigned maintenance tasks.",
        "permissions": {
            "dashboard": ["view"],
            "properties": ["view"],
            "units": ["view"],
            "maintenance": ["view", "create", "edit_assigned"],
        },
    },
}


@click.command("create-admin")
def create_admin():
    """Create the first RentalHub Administrator account."""

    try:
        # Create default roles without overwriting existing role settings.
        roles = {}

        for role_name, details in DEFAULT_ROLES.items():
            role = Role.query.filter_by(name=role_name).first()

            if role is None:
                role = Role(
                    name=role_name, # type: ignore
                    description=details["description"], # type: ignore
                    permissions=details["permissions"], # type: ignore
                )
                db.session.add(role)

            roles[role_name] = role

        db.session.flush()

        admin_role = roles["Administrator"]

        existing_admin = User.query.filter_by(
            role_id=admin_role.id
        ).first()

        if existing_admin:
            db.session.rollback()
            click.echo(
                "An Administrator account already exists. "
                "No account was created."
            )
            return

        click.echo("\nCreate the first RentalHub Administrator\n")

        username = click.prompt("Username").strip().lower()
        email = click.prompt("Email").strip().lower()

        if not username or not email:
            raise click.ClickException(
                "Username and email are required."
            )

        if User.query.filter_by(username=username).first():
            raise click.ClickException("That username already exists.")

        if User.query.filter_by(email=email).first():
            raise click.ClickException("That email already exists.")

        password = click.prompt(
            "Password",
            hide_input=True,
            confirmation_prompt=True,
        )

        if len(password) < 12:
            raise click.ClickException(
                "Password must contain at least 12 characters."
            )

        admin = User(
            username=username, # type: ignore
            email=email, # type: ignore
            role=admin_role, # type: ignore
            is_active=True, # type: ignore
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        click.echo(
            f"\nAdministrator account '{username}' created successfully."
        )

    except click.ClickException:
        db.session.rollback()
        raise

    except SQLAlchemyError:
        db.session.rollback()
        raise click.ClickException(
            "The Administrator account could not be created. "
            "Check the application logs."
        )


@click.command("reset-admin-password")
def reset_admin_password():
    """Reset an Administrator password locally."""

    try:
        admin_role = Role.query.filter_by(
            name="Administrator"
        ).first()

        if admin_role is None:
            raise click.ClickException(
                "Administrator role does not exist."
            )

        administrators = User.query.filter_by(
            role_id=admin_role.id
        ).order_by(User.username).all()

        if not administrators:
            raise click.ClickException(
                "No Administrator accounts were found."
            )

        click.echo("\nRentalHub Administrator Password Recovery\n")
        click.echo("Available Administrator accounts:")

        for admin in administrators:
            status = "Active" if admin.is_active else "Inactive"
            click.echo(f" - {admin.username} ({status})")

        username = click.prompt(
            "\nEnter Administrator username"
        ).strip().lower()

        admin = User.query.filter_by(
            username=username,
            role_id=admin_role.id
        ).first()

        if admin is None:
            raise click.ClickException(
                "Administrator account not found."
            )

        if not click.confirm(
            f"Reset the password for '{admin.username}'?"
        ):
            click.echo("Password recovery cancelled.")
            return

        password = click.prompt(
            "New password",
            hide_input=True,
            confirmation_prompt=True,
        )

        if len(password) < 12:
            raise click.ClickException(
                "Password must contain at least 12 characters."
            )

        admin.set_password(password)

        db.session.commit()

        click.echo(
            f"\nPassword successfully reset for '{admin.username}'."
        )

    except click.ClickException:
        db.session.rollback()
        raise

    except SQLAlchemyError:
        db.session.rollback()
        raise click.ClickException(
            "Password reset failed. Check the application logs."
        )
