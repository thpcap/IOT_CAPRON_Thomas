
from sqlalchemy import (
    String,
    Boolean,
    BigInteger,
    Integer,
    Numeric,
    DateTime,
    Enum,
    Text,
    ForeignKey,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.Database import Base


class SensorTable(Base):
    __tablename__ = "sensor"

    serialnumber: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False
    )
    
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    topic_t: Mapped[str] = mapped_column(String(150))
    topic_h: Mapped[str] = mapped_column(String(150))
    topic_date: Mapped[str] = mapped_column(String(150))
    topic_version: Mapped[str] = mapped_column(String(150))
    topic_command: Mapped[str] = mapped_column(String(150))
    topic_blink: Mapped[str] = mapped_column(String(150))
    topic_bargraph: Mapped[str] = mapped_column(String(150))

    version: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )

    autoimported: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


class Reading(Base):
    __tablename__ = "reading"

    read_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    SN: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sensor.serialnumber", ondelete="CASCADE"),
        nullable=False
    )

    type: Mapped[str] = mapped_column(
        Enum("T", "H", name="reading_type"),
        nullable=False
    )

    val: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    date: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )


class Conf(Base):
    __tablename__ = "conf"

    conf_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    key: Mapped[str] = mapped_column(
        "key", String(100), unique=True, nullable=False
    )

    value: Mapped[str | None] = mapped_column(
        "value", Text, nullable=True
    )
