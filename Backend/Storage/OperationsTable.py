from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Mapped,mapped_column,relationship
from Backend.Storage.Base import Base

class Operation(Base):
    """Model for operation info"""
    __tablename__ = 'operations'
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="operations")
    operation_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("operation_types.id"))
    operation_type = relationship("OperationType", back_populates="operation")
    status_id:Mapped[int] = mapped_column(Integer, ForeignKey("operation_statuses.id"))
    status = relationship("OperationStatus", back_populates="operation")
    progress: Mapped[float] = mapped_column(Float)
    def __repr__(self) -> str:
        return f"Operation(id={self.id!r}, type={self.operation_type.name!r}, status={self.status.name!r}, progress={self.progress!r})"
