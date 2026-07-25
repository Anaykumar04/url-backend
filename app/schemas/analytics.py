from pydantic import BaseModel
from datetime import datetime

class AnalyticsBase(BaseModel):
    ip_address: str | None = None
    user_agent: str | None = None
    country: str | None = None

class AnalyticsCreate(AnalyticsBase):
    url_id: int

class Analytics(AnalyticsBase):
    id: int
    url_id: int
    clicked_at: datetime

    class Config:
        from_attributes = True
