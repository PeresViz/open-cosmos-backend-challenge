from fastapi import FastAPI
from datetime import datetime

from api.decorators.requires_permissions import requires_permissions
from business_logic import BusinessLogic

app = FastAPI()
business_logic = BusinessLogic()


@app.get("/data")
@requires_permissions(["read_data"])
async def get_data(start_time: datetime = None, end_time: datetime = None):
    business_logic.process_and_store_data()
    return business_logic.get_data_with_filters(start_time, end_time)


@app.get("/discard_reasons")
@requires_permissions(["view_discard_reasons"])
async def get_discard_data():
    business_logic.process_and_store_data()
    return business_logic.get_discard_reasons()
