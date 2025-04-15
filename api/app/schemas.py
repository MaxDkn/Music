from pydantic import BaseModel
from typing import ClassVar

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
    artworkUrl100: str

    class Config:
        from_attrbiutes = True
