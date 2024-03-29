from functools import wraps

def fetch_data_from_server(business_logic):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            business_logic.fetch_data_from_server()
            return await func(*args, **kwargs)
        return wrapper
    return decorator