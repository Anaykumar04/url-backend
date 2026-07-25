from pydantic import BaseModel, HttpUrl
from datetime import datetime

class URLBase(BaseModel):
    original_url: HttpUrl

class URLCreate(URLBase):
    pass

class URLInfo(URLBase):
    id: int
    short_code: str
    clicks: int
    owner_id: int | None = None
    created_at: datetime
    short_url: str

    class Config:
        from_attributes = True
