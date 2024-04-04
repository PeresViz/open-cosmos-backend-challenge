from fastapi import HTTPException, Header
from datetime import datetime

from api.authorization.authorize_user import authorize_user
from api.authorization.roles import ROLES


def requires_permissions(required_permissions: list):
    def decorator(func):
        async def wrapper(api_key: str = Header(...), start_time: datetime = None, end_time: datetime = None):
            user_role = await authorize_user(api_key)
            if not set(required_permissions).issubset(ROLES.get(user_role, [])):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(start_time=start_time, end_time=end_time)
        return wrapper
    return decorator