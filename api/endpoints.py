from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import Optional

from api.constants import (
    READ_DATA_PERMISSION,
    VIEW_DATA_INVALIDATION_REASONS_PERMISSION,
    DATA_ENDPOINT,
    DATA_INVALIDATION_REASONS_ENDPOINT,
)
from api.decorators.requires_permissions import requires_permissions
from api.decorators.fetch_data_from_server import fetch_data_from_server
from business_logic.business_logic_factory import BusinessLogicFactory
from business_logic.exceptions.failure_retrieving_invalid_data_reasons_exception \
    import FailureRetrievingInvalidDataReasonsException
from business_logic.exceptions.failure_retrieving_data \
    import FailureRetrievingData
from models.data import Data
from models.data_invalidation_reasons import DataInvalidationReasons

app = FastAPI()
business_logic = BusinessLogicFactory.instantiate_business_logic()


@app.get(f"/{DATA_ENDPOINT}")
@fetch_data_from_server(business_logic)
@requires_permissions([READ_DATA_PERMISSION])
async def get_data(
        start_time: datetime = None,
        end_time: datetime = None,
) -> list[Optional[Data]]:
    try:
        return business_logic.get_data(start_time=start_time, end_time=end_time)
    except FailureRetrievingData as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}")
@fetch_data_from_server(business_logic)
@requires_permissions([VIEW_DATA_INVALIDATION_REASONS_PERMISSION])
async def get_discard_data(
        start_time: datetime = None,
        end_time: datetime = None,
) -> list[Optional[DataInvalidationReasons]]:
    try:
        return business_logic.get_reasons_for_invalid_data(start_time=start_time, end_time=end_time)
    except FailureRetrievingInvalidDataReasonsException as e:
        raise HTTPException(status_code=500, detail=str(e))
