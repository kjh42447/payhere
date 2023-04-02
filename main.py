from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
import jwt

from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engineconn
from models import User, UserCreate, Expenses, ExpensesCreate, ExpensesPatch

load_dotenv()

# db연동
engine = engineconn()
session = engine.sessionmaker()

# jwt
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.environ.get("SECRET_KEY")

# 토큰 헤더
api_key_header = APIKeyHeader(name="Authorization")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

@app.get("/")
def index():
    return {"fastapi": "framework"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 토큰 디코딩
def decode_token(token: str):
    try:
        # JWT 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = {"email": email, "user_id": user_id}
        return token_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 유저 정보 불러오는 함수
def get_users(db: Session):
    users = db.query(User).all()
    return users

# 유저 정보를 조회하는 함수
def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# 유저 정보를 조회하는 Depends 함수
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(engine.sessionmaker)):
    token_data = decode_token(token)
    email = token_data["email"]
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# 가계부 정보 조회
async def get_expenses(expense: ExpensesPatch, db:Session):
    expenses = db.query(Expenses).filter(Expenses.expenses_id == expense.expenses_id).first()
    if expenses is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return expenses

# 비밀번호를 해싱하는 함수
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# 비밀번호를 해싱하는 Depends 함수
async def get_password_hash(password):
    return pwd_context.hash(password)


# 토큰 생성 함수
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 회원가입 API
@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(engine.sessionmaker)):
    # 입력한 아이디로 유저 정보 조회
    existing_user = db.query(User).filter(User.email == user.email).first()
    # 이미 해당 아이디로 가입된 유저가 있으면 에러 반환
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # 비밀번호 해싱
    hashed_password = await get_password_hash(user.password)
    # 새로운 유저 생성
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # 생성한 유저 정보를 반환
    return new_user.jsonable()

# 로그인 API
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(engine.sessionmaker)):
    # 입력한 아이디로 유저 정보 조회
    user = authenticate_user(form_data.username, form_data.password, db)
    # 유저 정보가 없거나 비밀번호가 일치하지 않으면 에러 반환
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # 토큰 만료 시간 설정
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 토큰 생성
    access_token = create_access_token(
        data={"user_id": user.user_id, "sub": user.email}, expires_delta=access_token_expires
    )
    # 토큰 정보를 반환
    return {"access_token": access_token, "token_type": "bearer"}

# 유저 정보 조회 API
@app.get("/users")
async def read_users(db: Session = Depends(engine.sessionmaker)):
    users = get_users(db)
    return [user.jsonable() for user in users]

# 가계부 생성 API
@app.post("/expenses")
async def create_expenses(expenses: ExpensesCreate, db: Session = Depends(engine.sessionmaker), token: str = Depends(api_key_header)):
    decoded_token = decode_token(token[7:])
    email = decoded_token["email"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = decoded_token["user_id"]

    new_expenses = Expenses(cost=expenses.cost, comment=expenses.comment, user_id=user_id)
    db.add(new_expenses)
    db.commit()
    db.refresh(new_expenses)

    return new_expenses.jsonable()

# 가계부 수정 API
@app.patch("/expenses")
async def patch_expenses(expenses: ExpensesPatch, db: Session = Depends(engine.sessionmaker), token: str = Depends(api_key_header)):
    decoded_token = decode_token(token[7:])
    email = decoded_token["email"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expense = await get_expenses(expenses, db)

    if not expense:
        raise HTTPException(status_code=400, detail="Not in this expenses")

    expense.cost = expenses.cost
    expense.comment = expenses.comment
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense.jsonable()