from fastapi import FastAPI
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
    return business_logic.get_data(start_time=start_time, end_time=end_time)


@app.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}")
@fetch_data_from_server(business_logic)
@requires_permissions([VIEW_DATA_INVALIDATION_REASONS_PERMISSION])
async def get_discard_data(
        start_time: datetime = None,
        end_time: datetime = None,
) -> list[Optional[DataInvalidationReasons]]:
    return business_logic.get_reasons_for_invalid_data(start_time=start_time, end_time=end_time)
