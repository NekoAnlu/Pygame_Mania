# 游戏相关设置
from typing import Dict


class PlayerSetting:
    noteSpeed: int
    OD: int

class GameSetting:
    deltaTime: int

    # 屏幕大小 浮点方便计算
    screenWidth: float = 1920.0
    screenHeight: float = 1080.0

    # 判定设置 OD8
    timing_PPerfect = 16.5
    timing_Perfect = 40.5
    timing_Great = 73.5
    timing_Cool = 103.5
    timing_Bad = 127.5
    timing_Miss = 164


class ManiaUIModel:
    lineWidth: int = 120
    lineStart: int = 0
    noteSpawnPosition: int = -50
    noteDestination: int = 900
    judgementPosition: int = 500
    comboPosition: int = 300

    # judgementTextSpriteDict: Dict[str, JudgementTextSprite] = {}
    # variableTextList: Dict[str, VariableTextSprite] = {}  # 用于监控数值变化后调用对应sprite的update更新view