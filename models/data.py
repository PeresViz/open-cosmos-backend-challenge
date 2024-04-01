from pydantic import BaseModel


class Data(BaseModel):
    time: str
    value: list[int]
    tags: list[str]


