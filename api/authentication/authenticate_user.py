from fastapi import HTTPException


async def authenticate_user(api_key: str):
    if api_key == "admin_api_key":
        return "admin"
    elif api_key == "user_api_key":
        return "user"
    else:
        raise HTTPException(status_code=401, detail="Invalid API key")