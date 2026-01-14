import datetime
import uuid

from sqlalchemy import PrimaryKeyConstraint, UUID, String, Text, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.expression import text
from sqlalchemy.testing.schema import mapped_column

from app.infra.models.base import Base


class Demo(Base):
    """demo模型 用来演示alembic迁移功能"""
    __tablename__ = 'demo'
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_demo_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False, primary_key=True,
                                          server_default=text("uuid_generate_v4()"))
    name: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))
    avatar: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    updated_at = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        onupdate=datetime.datetime.now()
    )
    created_at = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"))
