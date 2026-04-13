from pydantic import BaseModel
from typing import List


class ServiceOptionSchema(BaseModel):
    name: str


class ServiceFieldSchema(BaseModel):
    field_name: str
    field_type: str


class ServiceCreate(BaseModel):
    key: str
    title: str
    color: str

    options: List[ServiceOptionSchema]
    fields: List[ServiceFieldSchema]
