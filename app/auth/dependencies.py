from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import UserResponse


def get_current_user(db, token: str):
    user_id = User.verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    return UserResponse.model_validate(user)

def get_current_active_user(current_user: UserResponse):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user