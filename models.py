from sqlalchemy import Column, TEXT, INT, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)
    email = Column(TEXT, nullable=False)

    def jsonable(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email
        }

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Expenses(Base):
    __tablename__ = "expenses"

    expenses_id = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    cost = Column(INT, nullable=False)
    comment = Column(TEXT, nullable=False)
    user_id = Column(INT, ForeignKey("users.user_id"))

    def jsonable(self):
        return {
            "expenses_id": self.expenses_id,
            "user_id": self.user_id,
            "cost": self.cost,
            "comment": self.comment
        }

class ExpensesCreate(BaseModel):
    user_id: int
    cost: int
    comment: str

class ExpensesPatch(BaseModel):
    expenses_id: int
    user_id: int
    cost: int
    comment: str