from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Mapped,mapped_column,relationship
from Storage.Base import Base

class ModelTraining(Base):
    __tablename__ = 'model_train'
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="model")
    num_epochs: Mapped[int] = mapped_column(Integer)
    batch_size: Mapped[int] = mapped_column(Integer)
    current_epoch: Mapped[int] = mapped_column(Integer, default=0)
    apc_acc: Mapped[float] = mapped_column(Float, default=0.0)
    apc_f1: Mapped[float] = mapped_column(Float, default=0.0)
    ate_f1: Mapped[float] = mapped_column(Float, default=0.0)
    def __repr__(self) -> str:
        return f"ModelTraining(id={self.id!r}, epochs={self.current_epoch!r}/{self.num_epochs!r}, APC_ACC:{self.apc_acc!r}|APC_F1:{self.apc_f1!r}|ATE_F1:{self.ate_f1!r})"
