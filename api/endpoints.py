from fastapi import FastAPI
from datetime import datetime

from api.decorators.requires_permissions import requires_permissions
from api.decorators.fetch_data_from_server import fetch_data_from_server
from business_logic.business_logic_factory import BusinessLogicFactory


app = FastAPI()
business_logic = BusinessLogicFactory.instantiate_business_logic()


@app.get("/data")
@fetch_data_from_server(business_logic)
@requires_permissions(["read_data"])
async def get_data(
        start_time: datetime = None,
        end_time: datetime = None,
):
    return business_logic.get_data(start_time=start_time, end_time=end_time)


@app.get("/discard_reasons")
@fetch_data_from_server(business_logic)
@requires_permissions(["view_discard_reasons"])
async def get_discard_data(
        start_time: datetime = None,
        end_time: datetime = None,
):
    return business_logic.get_reasons_for_invalid_data(start_time=start_time, end_time=end_time)
