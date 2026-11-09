"""Non-destructive baseline for the existing application schema.

This migration supports both fresh databases and databases whose tables were
created earlier by SQLAlchemy create_all(). Existing columns are validated;
the migration never drops or rewrites application data.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0001_existing_schema_baseline"
down_revision = None
branch_labels = None
depends_on = None


def _existing_columns(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _create_or_validate(table_name: str, required_columns: set[str], create_table) -> None:
    columns = _existing_columns(table_name)
    if not columns:
        create_table()
        columns = _existing_columns(table_name)
    missing = required_columns - columns
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise RuntimeError(
            f"Existing table {table_name!r} is missing expected columns: {missing_list}. "
            "No automatic repair was attempted."
        )


def upgrade() -> None:
    _create_or_validate(
        "enquiries",
        {
            "id", "name", "email", "phone", "property_address", "property_type",
            "approximate_size_sqft", "message", "preferred_dates", "status", "created_at",
        },
        lambda: op.create_table(
            "enquiries",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("email", sa.String(length=254), nullable=False),
            sa.Column("phone", sa.String(length=40), nullable=False),
            sa.Column("property_address", sa.String(length=300), nullable=False),
            sa.Column("property_type", sa.String(length=40), nullable=False),
            sa.Column("approximate_size_sqft", sa.Integer(), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("preferred_dates", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        ),
    )
    _create_or_validate(
        "booking_proposals",
        {"id", "enquiry_id", "option_1", "option_2", "option_3", "status", "created_at"},
        lambda: op.create_table(
            "booking_proposals",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("enquiry_id", sa.Integer(), nullable=False),
            sa.Column("option_1", sa.String(length=80), nullable=False),
            sa.Column("option_2", sa.String(length=80), nullable=False),
            sa.Column("option_3", sa.String(length=80), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        ),
    )
    indexes = {item["name"] for item in inspect(op.get_bind()).get_indexes("booking_proposals")}
    if "ix_booking_proposals_enquiry_id" not in indexes:
        op.create_index(
            "ix_booking_proposals_enquiry_id",
            "booking_proposals",
            ["enquiry_id"],
            unique=False,
        )


def downgrade() -> None:
    raise RuntimeError(
        "The initial baseline may represent pre-existing customer data and is intentionally non-reversible."
    )
