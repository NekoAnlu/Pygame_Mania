from src.Grahpic.ManiaSprite import *
from pygame import *
from typing import List, Tuple, Optional, Dict

from .BeatmapModel import *


class GameModel:
    songList: List[Song]

class LevelModel:
    # 按键基础数据
    noteSpeed: int = 1900

    # 当前关卡数据
    currentSong: Song
    currentChart: Chart
    timer: int = 0

    # 谱面数据
    noteList: List[List[Note]] = []
    noteSpritePool: NoteSpritePool = NoteSpritePool()
    lnSpritePool: LNSpritePool = LNSpritePool()
    noteQueue: List[List[NoteSprite | LNSprite]] = []  # 判定用
    totalNotes: int = 0

    # 背景
    backgroundImage: Surface


class ManiaUIModel:
    lineWidth: int = 120
    lineStart: int = 0
    noteSpawnPosition: int = -50
    noteDestination: int = 900
    judgementPosition: int = 500
    comboPosition: int = 300

    judgementTextSpriteDict: Dict[str, JudgementTextSprite] = {}
    variableTextList: Dict[str, VariableTextSprite] = {}  # 用于监控数值变化后调用对应sprite的update更新view


class PlayerModel:
    # 判定信息
    pPerfectCount: int = 0
    perfectCount: int = 0
    greatCount: int = 0
    coolCount: int = 0
    badCount: int = 0
    missCount: int = 0
    combo: int = 0
    maxCombo: int = 0
    score: int = 0
    accuracy: float = 0.0
    scoreBonus: int = 100
