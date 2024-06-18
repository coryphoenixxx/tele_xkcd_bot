from datetime import date

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    and_,
    false,
    func,
    true,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from api.infrastructure.database.constraints import (
    UNIQUE_COMIC_NUMBER_IF_NOT_EXTRA_CONSTRAINT,
    UNIQUE_COMIC_TITLE_IF_NOT_EXTRA_CONSTRAINT,
    UNIQUE_TRANSLATION_IF_NOT_DRAFT,
)


class BaseModel(DeclarativeBase):
    __abstract__ = True


BaseModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class TimestampMixin:
    created_at: Mapped[date] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[date] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )


class TranslationImageModel(BaseModel, TimestampMixin):
    __tablename__ = "translation_images"

    image_id: Mapped[int] = mapped_column(primary_key=True)
    translation_id: Mapped[int | None] = mapped_column(
        ForeignKey("translations.translation_id", ondelete="SET NULL"),
    )
    original_rel_path: Mapped[str]
    converted_rel_path: Mapped[str | None]
    thumbnail_rel_path: Mapped[str | None]

    translation: Mapped["TranslationModel"] = relationship(back_populates="images")

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(id={self.image_id}, original_rel_path={self.original_rel_path})"
        )

    def __repr__(self) -> str:
        return str(self)


class TranslationModel(BaseModel, TimestampMixin):
    __tablename__ = "translations"

    translation_id: Mapped[int] = mapped_column(primary_key=True)
    comic_id: Mapped[int] = mapped_column(ForeignKey("comics.comic_id", ondelete="CASCADE"))
    title: Mapped[str]
    language: Mapped[str] = mapped_column(String(2))
    tooltip: Mapped[str] = mapped_column(default="")
    raw_transcript: Mapped[str] = mapped_column(default="")
    translator_comment: Mapped[str] = mapped_column(default="")
    source_url: Mapped[str | None]
    is_draft: Mapped[bool] = mapped_column(default=False)
    images: Mapped[list["TranslationImageModel"]] = relationship(
        back_populates="translation",
        lazy="joined",
    )

    searchable_text: Mapped[str] = mapped_column(Text)

    comic: Mapped["ComicModel"] = relationship(back_populates="translations")

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(id={self.translation_id}, comic_id={self.comic_id}, "
            f"language={self.language}, title={self.title})"
        )

    def __repr__(self) -> str:
        return str(self)

    __table_args__ = (
        Index(
            UNIQUE_TRANSLATION_IF_NOT_DRAFT,
            "language",
            "comic_id",
            unique=True,
            postgresql_where=(~is_draft),
        ),
        Index(
            "ix_translations_searchable_text",
            "searchable_text",
            postgresql_using="pgroonga",
        ),
    )


class ComicTagAssociation(BaseModel):
    __tablename__ = "comic_tag_association"

    comic_id: Mapped[int] = mapped_column(
        ForeignKey("comics.comic_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True,
    )


class TagModel(BaseModel):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(unique=True)

    comics: Mapped[list["ComicModel"]] = relationship(
        back_populates="tags",
        secondary="comic_tag_association",
    )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.tag_id}, name={self.name})"

    def __repr__(self) -> str:
        return str(self)


class ComicModel(BaseModel, TimestampMixin):
    __tablename__ = "comics"

    comic_id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int | None] = mapped_column(SmallInteger)
    slug: Mapped[str]
    publication_date: Mapped[date]
    explain_url: Mapped[str | None]
    click_url: Mapped[str | None]
    is_interactive: Mapped[bool] = mapped_column(default=False)

    tags: Mapped[list["TagModel"]] = relationship(
        lazy="selectin",
        back_populates="comics",
        secondary="comic_tag_association",
        cascade="all, delete",
    )

    original: Mapped[TranslationModel] = relationship(
        lazy="selectin",
        back_populates="comic",
        primaryjoin=lambda: and_(
            ComicModel.comic_id == TranslationModel.comic_id,
            TranslationModel.is_draft == false(),
            TranslationModel.language == "EN",
        ),
    )

    translations: Mapped[list["TranslationModel"]] = relationship(
        lazy="selectin",
        back_populates="comic",
        cascade="all, delete",
        primaryjoin=lambda: and_(
            ComicModel.comic_id == TranslationModel.comic_id,
            TranslationModel.is_draft == false(),
            TranslationModel.language != "EN",
        ),
        overlaps="original",
    )

    translation_drafts: Mapped[list["TranslationModel"]] = relationship(
        lazy="selectin",
        back_populates="comic",
        cascade="all, delete",
        primaryjoin=lambda: and_(
            ComicModel.comic_id == TranslationModel.comic_id,
            TranslationModel.is_draft == true(),
            TranslationModel.language != "EN",
        ),
        overlaps="original,translations",
    )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(id={self.comic_id}, number={self.number}, slug={self.slug})"
        )

    def __repr__(self) -> str:
        return str(self)

    __table_args__ = (
        Index(
            UNIQUE_COMIC_NUMBER_IF_NOT_EXTRA_CONSTRAINT,
            "number",
            unique=True,
            postgresql_where=(number.isnot(None)),
        ),
        Index(
            UNIQUE_COMIC_TITLE_IF_NOT_EXTRA_CONSTRAINT,
            "slug",
            unique=True,
            postgresql_where=(number.is_(None)),
        ),
    )