from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    link: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False, index=True)
    guid: Mapped[str | None] = mapped_column(String(1000), unique=True, nullable=True, index=True)
    published: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ai_summary_record: Mapped["ArticleSummary | None"] = relationship(
        back_populates="article",
        uselist=False,
    )


class ArticleSummary(Base):
    __tablename__ = "article_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), unique=True, nullable=False)
    summary_ai: Mapped[str] = mapped_column(Text, nullable=False)
    bullets_ai: Mapped[str] = mapped_column(Text, nullable=False)
    summarized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    article: Mapped[Article] = relationship(back_populates="ai_summary_record")
