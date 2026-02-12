from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Constants
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')  # Should be set securely
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI()

# Mock database
dummy_users_db = {}  # This should ideally be a real database

class User(BaseModel):
    username: str
    email: str
    full_name: str = None
    disabled: bool = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create a new user
def create_user(username: str, password: str):
    if username in dummy_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    dummy_users_db[username] = UserInDB(
        username=username,
        email="email@example.com",
        hashed_password=pwd_context.hash(password)
    )

# Authenticate user
def authenticate_user(username: str, password: str):
    user = dummy_users_db.get(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# Generate JWT token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# MFA and session management should be implemented using appropriate libraries / services
# Additional endpoints for MFA verification and user management can be added here as per requirements