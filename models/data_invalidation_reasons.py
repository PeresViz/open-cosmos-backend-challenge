from pydantic import BaseModel


class DataInvalidationReasons(BaseModel):
    time: str
    reasons: list[str]
