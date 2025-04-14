from sqlalchemy import Column, Integer, String, LargeBinary
from .database import Base

class Music(Base):
    __tablename__ = "music"
    MusicId = Column(String, primary_key=True, index=True)
    Titre = Column(String)
    Artiste = Column(String)
    CoverImageBuffer = Column(LargeBinary)
    MusicBuffer = Column(LargeBinary)
