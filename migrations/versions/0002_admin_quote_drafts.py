"""Add administrator quote settings and draft quotes.

The application still invokes SQLAlchemy create_all() for demo compatibility.
This migration therefore tolerates the new tables already existing, while
validating their columns and ensuring the lookup index is present.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_admin_quote_drafts"
down_revision = "0001_existing_schema_baseline"
branch_labels = None
depends_on = None


def _ensure_table(name: str, columns: set[str], create_table) -> None:
    inspector = inspect(op.get_bind())
    existing = set()
    if name in inspector.get_table_names():
        existing = {column["name"] for column in inspector.get_columns(name)}
    if not existing:
        create_table()
        inspector = inspect(op.get_bind())
        existing = {column["name"] for column in inspector.get_columns(name)}
    missing = columns - existing
    if missing:
        raise RuntimeError(
            f"Existing table {name!r} is missing expected columns: {', '.join(sorted(missing))}. "
            "No automatic repair was attempted."
        )


def upgrade() -> None:
    _ensure_table(
        "quote_settings",
        {"id", "base_fee", "per_sqft_rate", "minimum_fee", "updated_at"},
        lambda: op.create_table(
            "quote_settings",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("base_fee", sa.Numeric(10, 2), nullable=True),
            sa.Column("per_sqft_rate", sa.Numeric(10, 4), nullable=True),
            sa.Column("minimum_fee", sa.Numeric(10, 2), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        ),
    )
    _ensure_table(
        "quote_drafts",
        {
            "id", "enquiry_id", "property_type", "size_sqft", "base_fee",
            "per_sqft_rate", "minimum_fee", "subtotal", "currency", "status",
            "note", "created_at",
        },
        lambda: op.create_table(
            "quote_drafts",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("enquiry_id", sa.Integer(), nullable=False),
            sa.Column("property_type", sa.String(length=40), nullable=False),
            sa.Column("size_sqft", sa.Integer(), nullable=False),
            sa.Column("base_fee", sa.Numeric(10, 2), nullable=False),
            sa.Column("per_sqft_rate", sa.Numeric(10, 4), nullable=False),
            sa.Column("minimum_fee", sa.Numeric(10, 2), nullable=False),
            sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
            sa.Column("currency", sa.String(length=3), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("note", sa.String(length=300), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        ),
    )
    indexes = {item["name"] for item in inspect(op.get_bind()).get_indexes("quote_drafts")}
    if "ix_quote_drafts_enquiry_id" not in indexes:
        op.create_index("ix_quote_drafts_enquiry_id", "quote_drafts", ["enquiry_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_quote_drafts_enquiry_id", table_name="quote_drafts")
    op.drop_table("quote_drafts")
    op.drop_table("quote_settings")
