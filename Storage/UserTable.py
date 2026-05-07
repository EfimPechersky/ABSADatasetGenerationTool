from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Mapped,mapped_column,relationship
from Storage.Base import Base
from typing import List
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(255))
    projects: Mapped[List["Project"]] = relationship(back_populates="user")
    access_token: Mapped[str] = mapped_column(String(255),nullable=True)
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, login={self.login!r}, email={self.email!r})"
