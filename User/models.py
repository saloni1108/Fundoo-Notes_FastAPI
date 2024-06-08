from typing import List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, Boolean, BigInteger, create_engine
from sqlalchemy.orm import DeclarativeBase, declarative_base, sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from Core.setting import settings

engine = create_engine(url = settings.DB_URL)

session = sessionmaker(bind = engine, autoflush = False, autocommit = False)

def get_db_session():
    db = session()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id:Mapped[int] = mapped_column(BigInteger, autoincrement = True, index = True, primary_key = True)
    user_name:Mapped[str] = mapped_column(String(length = 50), unique = True)
    password: Mapped[str] = mapped_column(String(length = 250))
    first_name: Mapped[str] = mapped_column(String(length = 20))
    last_name:Mapped[str] = mapped_column(String(length = 20))
    email: Mapped[str] = mapped_column(String(length = 100))
    is_verified: Mapped[bool] = mapped_column(Boolean, default = False) 

   
