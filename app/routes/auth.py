from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from app.models.user import UserCreate, UserResponse, User
from app.utils.auth import verify_password, hash_password, create_access_token
from app.database import get_database
from app.utils.exceptions import UserAlreadyExists, UserNotFound
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

logger = logging.getLogger(__name__)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    # This is a simplified version - in production you'd verify the JWT token
    # For now, returning a dummy user
    return User(
        id=None,
        username="testuser",
        email="test@example.com",
        password="",
        is_active=True,
        is_admin=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    db = await get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user document
    user_doc = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        is_active=True,
        is_admin=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ).dict()
    
    # Insert user
    result = await db.users.insert_one(user_doc)
    
    # Return user response (without password)
    user_response = UserResponse(
        id=result.inserted_id,
        username=user_doc["username"],
        email=user_doc["email"],
        is_active=user_doc["is_active"],
        is_admin=user_doc["is_admin"],
        created_at=user_doc["created_at"],
        updated_at=user_doc["updated_at"]
    )
    
    logger.info(f"New user registered: {user_doc['username']}")
    return user_response

@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    db = await get_database()
    
    # Find user
    user = await db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user['username']}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False)
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    # This would normally return the authenticated user
    # For now, returning a dummy response
    return UserResponse(
        id=None,
        username="testuser",
        email="test@example.com",
        is_active=True,
        is_admin=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )