from typing import List, Tuple, Optional
from enum import Enum


class Note:
    line: int
    startTiming: float
    endTiming: Optional[float] = None
    noteType: int  # 0 rice 1 ln


class Chart:
    creator: str
    version: str
    columnNum: int
    noteNum: int
    previewTime: int = 0
    audioPath: str
    offset: int = 0
    backgroundPath: str
    filePath: str
    bpmList: List[Tuple[float, float]]  # bpm timing
    noteList: List[Note]


class Song:
    title: str
    artist: str
    titleOrg: Optional[str] = None
    artistOrg: Optional[str] = None
    charts: List[Chart]
