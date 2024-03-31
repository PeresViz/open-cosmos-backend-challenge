from fastapi import HTTPException, Depends
from datetime import datetime

from api.authentication.authenticate_user import authenticate_user
from api.authentication.roles import ROLES


def requires_permissions(required_permissions: list):
    def decorator(func):
        async def wrapper(user_role: str = Depends(authenticate_user), start_time: datetime = None, end_time: datetime = None):
            if not set(required_permissions).issubset(ROLES.get(user_role, [])):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(start_time=start_time, end_time=end_time)
        return wrapper
    return decorator