from src.Grahpic.ManiaSprite import *
from pygame import *
from typing import List, Tuple, Optional, Dict

from .BeatmapModel import *


class GameModel:
    songDict: Dict[str, Song] = {}
    selectedChart: Chart = None
    gameLoop: str = 'Title'
    isGamePause: bool = False


class LevelModel:
    def __init__(self):
        # 按键基础数据
        self.currentChart = None
        self.backgroundImage = None
        self.noteSpeed: int = 2000

        # 当前关卡数据
        self.currentSong: Song
        self.currentChart: Chart
        self.timer: int = 0

        # 谱面数据
        self.noteList: List[List[Note]] = []
        self.noteSpritePool: NoteSpritePool = NoteSpritePool()
        self.lnSpritePool: LNSpritePool = LNSpritePool()
        self.noteQueue: List[List[NoteSprite | LNSprite]] = []  # 判定用
        self.totalNotes: int = 0
        self.lineIndex: List[int] = []
        self.leadInTime: int = 2000
        self.leadOutTime: int = 1000
        self.firstNoteTiming: float = 10000000

        # 背景
        self.backgroundImage: Surface


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
    def __init__(self):
        # 判定信息
        self.pPerfectCount: int = 0
        self.perfectCount: int = 0
        self.greatCount: int = 0
        self.coolCount: int = 0
        self.badCount: int = 0
        self.missCount: int = 0
        self.combo: int = 0
        self.maxCombo: int = 0
        self.score: int = 0
        self.accuracy: float = 0.0
        self.scoreBonus: int = 100
        self.fastCount: int = 0
        self.lateCount: int = 0
