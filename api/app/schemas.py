from pydantic import BaseModel
from typing import ClassVar

class MusicIdResponse(BaseModel):
    MusicId: str

    class Config:
        from_attributes = True


class MusicResponse(MusicIdResponse):
    Titre: str
    Artiste: str
    CoverImageBuffer: ClassVar[bytes]
    MusicBuffer: ClassVar[bytes]
