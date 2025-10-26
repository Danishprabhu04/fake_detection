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

class AnalysisResult(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    video_id: str
    analysis_type: str  # "video", "comments", "combined"
    risk_score: float = 0.0
    confidence_score: float = 0.0
    fake_news_probability: float = 0.0
    sentiment_analysis: Dict[str, Any] = {}
    keyword_analysis: Dict[str, Any] = {}
    thumbnail_analysis: Dict[str, Any] = {}
    transcript_analysis: Dict[str, Any] = {}
    comment_analysis: Dict[str, Any] = {}
    red_flags: List[str] = []
    sources_verified: bool = False
    fact_check_results: List[Dict[str, Any]] = []
    analysis_summary: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True  # Changed from allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AnalysisCreate(BaseModel):
    video_id: str
    analysis_type: str = "combined"

class AnalysisResponse(BaseModel):
    id: PyObjectId
    video_id: str
    analysis_type: str
    risk_score: float
    confidence_score: float
    fake_news_probability: float
    sentiment_analysis: Dict[str, Any]
    keyword_analysis: Dict[str, Any]
    thumbnail_analysis: Dict[str, Any]
    transcript_analysis: Dict[str, Any]
    comment_analysis: Dict[str, Any]
    red_flags: List[str]
    sources_verified: bool
    fact_check_results: List[Dict[str, Any]]
    analysis_summary: str
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}