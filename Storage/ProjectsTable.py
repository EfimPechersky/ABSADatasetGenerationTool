from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Mapped,mapped_column,relationship
import datetime
from sqlalchemy import DateTime
from Storage.Base import Base
from sqlalchemy import func
class Project(Base):
    __tablename__ = 'projects'
    id: Mapped[int] = mapped_column(primary_key=True,  autoincrement=True)
    name: Mapped[str] = mapped_column(String(60))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user:Mapped["User"] = relationship(back_populates="projects")
    operations = relationship("Operation", back_populates="project")
    model = relationship("ModelTraining", back_populates="project")
    queue = relationship("Queue", back_populates="project")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    dir_name: Mapped[str] = mapped_column(String(255))
    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r}, user_id={self.user_id!r}, created_at={self.created_at!r}, dir={self.dir_name!r})"
    