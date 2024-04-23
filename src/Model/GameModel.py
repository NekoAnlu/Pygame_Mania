from src.Model.BeatmapModel import *
from src.Grahpic.ManiaSprite import *
from pygame import *
from typing import List, Tuple, Optional, Dict

class LevelModel:
    # 按键基础数据
    noteSpeed: int = 2000

    # 当前关卡数据
    currentSong: Song
    currentChart: Chart
    timer: int = 0

    # 谱面数据
    noteList: List[List[Note]] = []
    noteSpritePool: NoteSpritePool = NoteSpritePool()
    noteQueue: List[List[NoteSprite]] = []  # 判定用

    LNSpritePool: LNSpritePool = LNSpritePool()

    # 背景
    backgroundImage: Surface


class ManiaUIModel:
    lineWidth: int = 120
    lineStart: int = 800
    noteSpawnPosition: int = -50
    noteDestination: int = 900
    judgementPosition: int = 500
    comboPosition: int = 300

    judgementTextSpriteDict: Dict[str, JudgementTextSprite] = {}
    variableTextList: Dict[str, VariableTextSprite] = {}  # 用于监控数值变化后调用对应sprite的update更新view

class PlayerModel:
    combo: int = 0
