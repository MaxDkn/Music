from pydantic import BaseModel
from typing import Optional

class MusicIdResponse(BaseModel):
    trackId: int

    class Config:
        from_attributes = True


class MusicDBResponse(MusicIdResponse):
    trackName: str
    artisteName: str
    coverImageUrl: str
    

class ITunesResponse(BaseModel):
    trackId: int
    trackName: str
    artistId: int
    artistName: str
    artworkUrl: str
    statusCode: int
    statusDescription: Optional[str] = None

    class Config:
        from_attrbiutes = True
