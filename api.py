from fastapi import FastAPI, Query, HTTPException, Depends
from datetime import datetime
from business_logic import BusinessLogic

app = FastAPI()
business_logic = BusinessLogic()

ROLES = {
    "admin": ["read_data", "view_discard_reasons"],
    "user": ["read_data"]
}


async def authenticate_user(api_key: str = Query(...)):
    if api_key == "admin_api_key":
        return "admin"
    elif api_key == "user_api_key":
        return "user"
    else:
        raise HTTPException(status_code=401, detail="Invalid API key")


def check_permissions(required_permissions: list, user_role: str = Depends(authenticate_user)):
    if not set(required_permissions).issubset(ROLES.get(user_role, [])):
        raise HTTPException(status_code=403, detail="Insufficient permissions")


@app.get("/data")
async def get_data(start_time: datetime = None, end_time: datetime = None, user_role: str = Depends(authenticate_user)):
    business_logic.process_and_store_data()
    check_permissions(["read_data"], user_role)
    data = business_logic.get_data_with_filters(start_time, end_time)
    return data


@app.get("/discard_reasons")
async def get_discard_data(user_role: str = Depends(authenticate_user)):
    business_logic.process_and_store_data()
    check_permissions(["view_discard_reasons"], user_role)
    discard_reasons = business_logic.get_discard_reasons()
    return discard_reasons
