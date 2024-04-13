"""Initial

Revision ID: bfbb72709ca4
Revises:
Create Date: 2024-04-10 20:20:45.153454

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "bfbb72709ca4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(text("CREATE EXTENSION IF NOT EXISTS pgroonga;"))

    op.create_table(
        "comics",
        sa.Column("comic_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.SmallInteger(), nullable=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("publication_date", sa.Date(), nullable=False),
        sa.Column("explain_url", sa.String(), nullable=True),
        sa.Column("link_on_click", sa.String(), nullable=True),
        sa.Column("is_interactive", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("comic_id", name=op.f("pk_comics")),
    )
    op.create_index(
        "uq_number_if_not_extra",
        "comics",
        ["number"],
        unique=True,
        postgresql_where=sa.text("number IS NOT NULL"),
    )
    op.create_index(
        "uq_title_if_extra",
        "comics",
        ["slug"],
        unique=True,
        postgresql_where=sa.text("number IS NULL"),
    )
    op.create_table(
        "tags",
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("tag_id", name=op.f("pk_tags")),
        sa.UniqueConstraint("name", name=op.f("uq_tags_name")),
    )
    op.create_table(
        "comic_tag_association",
        sa.Column("comic_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["comic_id"],
            ["comics.comic_id"],
            name=op.f("fk_comic_tag_association_comic_id_comics"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.tag_id"],
            name=op.f("fk_comic_tag_association_tag_id_tags"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("comic_id", "tag_id", name=op.f("pk_comic_tag_association")),
    )
    op.create_table(
        "translations",
        sa.Column("translation_id", sa.Integer(), nullable=False),
        sa.Column("comic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("language", sa.String(length=2), nullable=False),
        sa.Column("tooltip", sa.String(), nullable=False),
        sa.Column("raw_transcript", sa.String(), nullable=False),
        sa.Column("translator_comment", sa.String(), nullable=False),
        sa.Column("source_link", sa.String(), nullable=True),
        sa.Column("is_draft", sa.Boolean(), nullable=False),
        sa.Column("searchable_text", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["comic_id"],
            ["comics.comic_id"],
            name=op.f("fk_translations_comic_id_comics"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("translation_id", name=op.f("pk_translations")),
    )
    op.create_index(
        "ix_translations_searchable_text",
        "translations",
        ["searchable_text"],
        unique=False,
        postgresql_using="pgroonga",
    )
    op.create_index(
        "uq_translation_if_not_draft",
        "translations",
        ["language", "comic_id"],
        unique=True,
        postgresql_where=sa.text("NOT is_draft"),
    )
    op.create_table(
        "translation_images",
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("translation_id", sa.Integer(), nullable=True),
        sa.Column("original_rel_path", sa.String(), nullable=False),
        sa.Column("converted_rel_path", sa.String(), nullable=True),
        sa.Column("thumbnail_rel_path", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["translation_id"],
            ["translations.translation_id"],
            name=op.f("fk_translation_images_translation_id_translations"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("image_id", name=op.f("pk_translation_images")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("translation_images")
    op.drop_index(
        "uq_translation_if_not_draft",
        table_name="translations",
        postgresql_where=sa.text("NOT is_draft"),
    )
    op.drop_index(
        "ix_translations_searchable_text", table_name="translations", postgresql_using="pgroonga",
    )
    op.drop_table("translations")
    op.drop_table("comic_tag_association")
    op.drop_table("tags")
    op.drop_index(
        "uq_title_if_extra", table_name="comics", postgresql_where=sa.text("number IS NULL"),
    )
    op.drop_index(
        "uq_number_if_not_extra",
        table_name="comics",
        postgresql_where=sa.text("number IS NOT NULL"),
    )
    op.drop_table("comics")
    # ### end Alembic commands ###