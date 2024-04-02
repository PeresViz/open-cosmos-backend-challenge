from pydantic import BaseModel


class Data(BaseModel):
    time: str
    value: float
    tags: list[str]


