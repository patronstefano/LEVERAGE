"""replace athlete birth year

Revision ID: 0010_replace_athlete_birth_year
Revises: 0009_add_reviewed_value_to_data_suggestions
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010_replace_athlete_birth_year"
down_revision: Union[str, None] = "0009_add_reviewed_value_to_data_suggestions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_COLUMN = "birth_year"
OLD_COLUMN = "birth" + "_" + "date"
YEAR_CHECK = "birth_year IS NULL OR (birth_year >= 1900 AND birth_year <= 2100)"
YEAR_CHECK_NAME = "ck_athletes_birth_year_valid"


def table_columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def table_check_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {constraint.get("name") for constraint in inspector.get_check_constraints(table_name)}


def upgrade() -> None:
    columns = table_columns("athletes")
    if NEW_COLUMN not in columns:
        with op.batch_alter_table("athletes") as batch_op:
            batch_op.add_column(sa.Column(NEW_COLUMN, sa.Integer(), nullable=True))

    columns = table_columns("athletes")
    if OLD_COLUMN in columns:
        op.execute(
            sa.text(
                f"""
                UPDATE athletes
                SET {NEW_COLUMN} = CAST(strftime('%Y', {OLD_COLUMN}) AS INTEGER)
                WHERE {NEW_COLUMN} IS NULL AND {OLD_COLUMN} IS NOT NULL
                """
            )
        )
        with op.batch_alter_table("athletes") as batch_op:
            batch_op.drop_column(OLD_COLUMN)

    if YEAR_CHECK_NAME not in table_check_names("athletes"):
        with op.batch_alter_table("athletes") as batch_op:
            batch_op.create_check_constraint(YEAR_CHECK_NAME, YEAR_CHECK)

    op.execute(
        sa.text(
            """
            UPDATE data_suggestions
            SET field_name = :new_column
            WHERE field_name = :old_column
            """
        ).bindparams(new_column=NEW_COLUMN, old_column=OLD_COLUMN)
    )
    op.execute(
        sa.text(
            """
            UPDATE data_suggestions
            SET suggested_value = substr(suggested_value, 1, 4)
            WHERE field_name = :new_column
              AND length(suggested_value) >= 4
            """
        ).bindparams(new_column=NEW_COLUMN)
    )
    op.execute(
        sa.text(
            """
            UPDATE data_suggestions
            SET reviewed_value = substr(reviewed_value, 1, 4)
            WHERE field_name = :new_column
              AND reviewed_value IS NOT NULL
              AND length(reviewed_value) >= 4
            """
        ).bindparams(new_column=NEW_COLUMN)
    )


def downgrade() -> None:
    columns = table_columns("athletes")
    if OLD_COLUMN not in columns:
        with op.batch_alter_table("athletes") as batch_op:
            batch_op.add_column(sa.Column(OLD_COLUMN, sa.Date(), nullable=True))

    columns = table_columns("athletes")
    if NEW_COLUMN in columns:
        op.execute(
            sa.text(
                f"""
                UPDATE athletes
                SET {OLD_COLUMN} = date({NEW_COLUMN} || '-01-01')
                WHERE {NEW_COLUMN} IS NOT NULL AND {OLD_COLUMN} IS NULL
                """
            )
        )
        if YEAR_CHECK_NAME in table_check_names("athletes"):
            with op.batch_alter_table("athletes") as batch_op:
                batch_op.drop_constraint(YEAR_CHECK_NAME, type_="check")
        with op.batch_alter_table("athletes") as batch_op:
            batch_op.drop_column(NEW_COLUMN)

    op.execute(
        sa.text(
            """
            UPDATE data_suggestions
            SET field_name = :old_column
            WHERE field_name = :new_column
            """
        ).bindparams(new_column=NEW_COLUMN, old_column=OLD_COLUMN)
    )
