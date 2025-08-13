from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PostResponse(BaseModel):
    id: int
    url: str
    site: str
    title: Optional[str]
    text: Optional[str]
    tags: List[str]
    time_public: Optional[datetime]
    time_stamp: Optional[datetime]
    photos: List[str]
