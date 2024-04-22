from src.Model.BeatmapModel import *
from src.Grahpic.ManiaSprite import *
from pygame import *
from typing import List, Tuple, Optional


class GameModel:
    deltaTime: int


class LevelModel:
    # 按键基础数据
    noteSpeed: int = 2000

    # 当前关卡数据
    currentSong: Song
    currentChart: Chart
    timer: int = 0

    # 谱面数据
    noteQueue: List[List[Note]] = []
    noteSpritePool: NoteSpritePool = NoteSpritePool()

    # 背景
    backgroundImage: Surface


class ManiaUIModel:
    lineWidth: int = 120
    lineStart: int = 800
    noteSpawnPosition: int = -50
    noteDestination: int = 900

