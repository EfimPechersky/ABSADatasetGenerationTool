from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
from Storage.Base import Base

class Queue(Base):
    __tablename__ = 'queue'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    num_epochs: Mapped[int] = mapped_column(Integer)
    batch_size: Mapped[int] = mapped_column(Integer)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # relationship использует строковое имя класса
    project = relationship("Project", back_populates="queue")
    
    def __repr__(self) -> str:
        return f"Queue(id={self.id!r}, project_id={self.project_id!r}, is_completed={self.is_completed!r})"