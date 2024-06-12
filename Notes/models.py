from typing import List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, Boolean, BigInteger, create_engine, DateTime
from sqlalchemy.orm import DeclarativeBase, declarative_base, sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from setting import settings
from datetime import datetime

engine = create_engine(url = settings.DB_URL_NOTES)

session = sessionmaker(bind = engine, autoflush = False, autocommit = False)

def get_db_session():
    db = session()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class Notes(Base):
    __tablename__ = "notes"

    id:Mapped[int] = mapped_column(Integer, autoincrement = True, index = True, primary_key = True)
    title:Mapped[str] = mapped_column(String(length = 50))
    description: Mapped[str] = mapped_column(String(length = 500))
    color: Mapped[str] = mapped_column(String(length = 20))
    reminder:Mapped[datetime] = mapped_column(DateTime, nullable = True, )
    is_archive: Mapped[bool] = mapped_column(Boolean, default = False)
    is_trash: Mapped[bool] = mapped_column(Boolean, default = False) 
    user_id: Mapped[int] = mapped_column(BigInteger, nullable= False)

class Labels(Base):
    __tablename__ = "labels"

    id:Mapped[int] = mapped_column(Integer, autoincrement = True, index = True, primary_key = True)
    label_name:Mapped[str] = mapped_column(String(length = 50)) 
    user_id: Mapped[int] = mapped_column(BigInteger, nullable= False)