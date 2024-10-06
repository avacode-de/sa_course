import datetime
from sqlalchemy import TIMESTAMP, Table, Column, Integer, String, MetaData, ForeignKey, text, Enum, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base, str_256
from typing import Annotated
import enum

intpk = Annotated[int, mapped_column(primary_key = True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("(datetime('now'))"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("(datetime('now'))"),
        onupdate=datetime.datetime.utcnow,
    )]

class WorkersOrm(Base):
    __tablename__ = "workers"

    id: Mapped[intpk]
    username: Mapped[str]

    resumes: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
    )

    resumes_parttime: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id == ResumesOrm.worker_id, ResumesOrm.workload == 'parttime')",
        order_by="ResumesOrm.id.desc()",
    )

class WorkLoadOrm(enum.Enum):
    parttime = "parttime"
    fulltime = "fulltime"

class ResumesOrm(Base):
    __tablename__ = "resumes"

    id: Mapped[intpk]
    title: Mapped[str_256]
    compensation: Mapped[int] = mapped_column(nullable=True) #can equals Null also
    workload: Mapped[WorkLoadOrm]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE")) #ForeignKey may bind few models
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    worker: Mapped["WorkersOrm"] = relationship(
        back_populates="resumes"
    )

    repr_cols_num = 4
    repr_cols = ("created_at", ) 

    __table_args__ = (
        Index("title_index", "title"),
        CheckConstraint("compensation > 0", name="checl_compensation_positive"),
    )




















metadata_obj = MetaData()

workers_table = Table(
    "workers",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String),
)

resumes_table = Table(
    "resumes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String(256)),
    Column("compensation", Integer, nullable=True),
    Column("workload", Enum(WorkLoadOrm)),
    Column("worker_id", ForeignKey("workers.id", ondelete="CASCADE")),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow),
)

