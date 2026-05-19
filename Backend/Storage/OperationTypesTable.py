from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Mapped,mapped_column,relationship
from Backend.Storage.Base import Base

class OperationType(Base):
    """Model for operation type info"""
    __tablename__ = 'operation_types'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    operation = relationship("Operation", back_populates="operation_type")
