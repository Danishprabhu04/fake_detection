from pydantic import BaseModel, Field
from typing import Optional, List
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

class Comment(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    video_id: str
    comment_id: str
    author: str
    text: str
    likes: int = 0
    replies: int = 0
    published_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    toxicity_score: Optional[float] = None
    keywords: List[str] = []
    flagged: bool = False
    flag_reasons: List[str] = []

    class Config:
        populate_by_name = True  # Changed from allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CommentCreate(BaseModel):
    video_id: str
    comment_id: str
    author: str
    text: str
    published_at: datetime

class CommentUpdate(BaseModel):
    text: Optional[str] = None
    likes: Optional[int] = None
    flagged: Optional[bool] = None
    flag_reasons: Optional[List[str]] = None

class CommentResponse(BaseModel):
    id: PyObjectId
    video_id: str
    comment_id: str
    author: str
    text: str
    likes: int
    replies: int
    published_at: datetime
    updated_at: datetime
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    toxicity_score: Optional[float]
    keywords: List[str]
    flagged: bool
    flag_reasons: List[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}