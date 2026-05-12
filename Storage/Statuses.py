from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Mapped,mapped_column,relationship
from Storage.Base import Base

class OperationStatus(Base):
    """Model for operation status info"""
    __tablename__ = 'operation_statuses'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    operation = relationship("Operation", back_populates="status")
