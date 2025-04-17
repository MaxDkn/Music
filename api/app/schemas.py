from pydantic import BaseModel
from typing import Optional

class MusicIdResponse(BaseModel):
    trackId: int

    class Config:
        from_attributes = True


class MusicDBResponse(MusicIdResponse):
    trackName: str
    artistName: str
    coverImageUrl: str
    

class ITunesResponse(MusicDBResponse):
    artistId: int
    statusCode: int
    statusDescription: Optional[str] = None

    class Config:
        from_attrbiutes = True
