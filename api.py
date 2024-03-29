from fastapi import FastAPI, Query, HTTPException, Depends
from datetime import datetime
from business_logic import BusinessLogic

app = FastAPI()
business_logic = BusinessLogic()

# Define roles and their associated permissions (for demonstration purposes)
ROLES = {
    "admin": ["read_data", "view_discard_reasons"],
    "user": ["read_data"]
}


# Mock function to authenticate users and determine their role based on API key
async def authenticate_user(api_key: str = Query(...)):
    # You need to implement your own authentication logic here
    # For demonstration purposes, let's assume the API key determines the user's role
    if api_key == "admin_api_key":
        return "admin"
    elif api_key == "user_api_key":
        return "user"
    else:
        raise HTTPException(status_code=401, detail="Invalid API key")

# Custom dependency to check if user is authorized based on their role


def check_permissions(required_permissions: list, user_role: str = Depends(authenticate_user)):
    if not set(required_permissions).issubset(ROLES.get(user_role, [])):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

# API endpoint to get data


@app.get("/data")
async def get_data(start_time: datetime = None, end_time: datetime = None, user_role: str = Depends(authenticate_user)):
    # Check if user is authorized to read data
    business_logic.process_and_store_data()
    check_permissions(["read_data"], user_role)
    data = business_logic.get_data_with_filters(start_time, end_time)
    return data


# API endpoint to get discard reasons (restricted to admin role)
@app.get("/discard_reasons")
async def get_discard_data(user_role: str = Depends(authenticate_user)):
    business_logic.process_and_store_data()
    # Check if user is authorized to view discard reasons
    check_permissions(["view_discard_reasons"], user_role)
    discard_reasons = business_logic.get_discard_reasons()
    return discard_reasons
