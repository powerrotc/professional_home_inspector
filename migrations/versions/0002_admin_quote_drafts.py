"""Add administrator quote settings and draft quotes."""
from alembic import op
import sqlalchemy as sa

revision = "0002_admin_quote_drafts"
down_revision = "0001_existing_schema_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quote_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("base_fee", sa.Numeric(10, 2), nullable=True),
        sa.Column("per_sqft_rate", sa.Numeric(10, 4), nullable=True),
        sa.Column("minimum_fee", sa.Numeric(10, 2), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
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
    )
    op.create_index("ix_quote_drafts_enquiry_id", "quote_drafts", ["enquiry_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_quote_drafts_enquiry_id", table_name="quote_drafts")
    op.drop_table("quote_drafts")
    op.drop_table("quote_settings")
