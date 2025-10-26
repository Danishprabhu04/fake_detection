from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                ),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

class Report(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    video_id: str
    report_type: str  # "detailed", "summary", "export"
    title: str
    content: str
    summary: str
    risk_level: str  # "low", "medium", "high", "critical"
    generated_by: Optional[str] = None  # user_id
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    format: str = "json"  # json, csv, pdf
    metadata: Dict[str, Any] = {}

    class Config:
        populate_by_name = True  # Changed from allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ReportCreate(BaseModel):
    video_id: str
    report_type: str = "detailed"
    format: str = "json"

class ReportResponse(BaseModel):
    id: PyObjectId
    video_id: str
    report_type: str
    title: str
    content: str
    summary: str
    risk_level: str
    generated_by: Optional[str]
    generated_at: datetime
    format: str
    metadata: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}