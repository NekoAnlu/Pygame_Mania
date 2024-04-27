from typing import List, Tuple, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Note(BaseModel):
    line: int
    startTiming: float
    endTiming: Optional[float] = None
    noteType: int  # 0 rice 1 ln


class Chart(BaseModel):
    creator: str
    version: str
    noteNum: int
    previewTime: int = 0
    audioPath: str
    offset: int = 0
    backgroundPath: str
    filePath: str
    bpmList: List[Tuple[float, float]]  # bpm timing
    noteList: List[Note]


class Song(BaseModel):
    title: str
    artist: str
    titleOrg: Optional[str] = None
    artistOrg: Optional[str] = None
    charts: List[Chart]
