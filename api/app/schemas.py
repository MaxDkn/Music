from pydantic import BaseModel
from typing import ClassVar

class MusicIdResponse(BaseModel):
    MusicId: str

    class Config:
        from_attributes = True


class MusicDBResponse(MusicIdResponse):
    Titre: str
    Artiste: str
    CoverImageBuffer: ClassVar[bytes]
    MusicBuffer: ClassVar[bytes]


class ITunesResponse(BaseModel):
    trackId: int
    trackName: str
    artistId: int
    artistName: str
    artworkUrl100: str

    class Config:
        from_attrbiutes = True
