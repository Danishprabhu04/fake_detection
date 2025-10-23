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

class Video(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    video_id: str = Field(..., description="YouTube video ID")
    title: str
    description: Optional[str] = None
    channel_title: str
    publish_date: Optional[datetime] = None
    duration: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    thumbnail_url: Optional[str] = None
    tags: List[str] = []
    category: Optional[str] = None
    language: Optional[str] = "en"
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True  # Changed from allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class VideoCreate(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    title: str
    description: Optional[str] = None
    channel_title: str
    thumbnail_url: Optional[str] = None
    tags: List[str] = []

class VideoResponse(BaseModel):
    id: PyObjectId
    video_id: str
    title: str
    description: Optional[str]
    channel_title: str
    publish_date: Optional[datetime]
    duration: Optional[str]
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
    thumbnail_url: Optional[str]
    tags: List[str]
    category: Optional[str]
    language: Optional[str]
    added_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}