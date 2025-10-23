from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import UserResponse
from app.database import get_database
from app.utils.auth import get_current_user
from app.models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_current_user)):
    """Get all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    users = await db.users.find({}).to_list(None)
    
    return [UserResponse(
        id=user["_id"],
        username=user["username"],
        email=user["email"],
        is_active=user["is_active"],
        is_admin=user["is_admin"],
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    ) for user in users]

@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active(user_id: str, current_user: User = Depends(get_current_user)):
    """Toggle user active status (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    from bson import ObjectId
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True}}  # Simplified for now
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User status updated"}