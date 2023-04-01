from sqlalchemy import Column, TEXT, INT, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    user_id = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)
    email = Column(TEXT, nullable=False)

class Expenses(Base):
    __tablename__ = "expenses"

    expenses = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    cost = Column(INT, nullable=False)
    comment = Column(TEXT, nullable=False)
    user_id = Column(INT, ForeignKey('user.user_id'))