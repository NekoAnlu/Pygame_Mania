# 游戏相关设置
from typing import List, Dict, Tuple, Sequence


class GameSetting:
    deltaTime: int

    # 屏幕大小 浮点方便计算
    screenWidth: float = 1920.0
    screenHeight: float = 1080.0

    # 判定设置 ScoreV1
    # https://osu.ppy.sh/wiki/zh/Gameplay/Judgement/osu%21mania
    timing_PPerfect = 16
    timing_Perfect = 64
    timing_Great = 97
    timing_Cool = 127
    timing_Bad = 151
    timing_Miss = 188

    def __init__(self):
        self.noteSpeed: int = 18
        self.OD: int = 8
        self.offset: int = 0
        self.cal_judgement_timing()

    def cal_judgement_timing(self):
        self.timing_PPerfect = 16
        self.timing_Perfect = 64 - 3 * self.OD
        self.timing_Great = 97 - 3 * self.OD
        self.timing_Cool = 127 - 3 * self.OD
        self.timing_Bad = 151 - 3 * self.OD
        self.timing_Miss = 188 - 3 * self.OD


class ManiaSetting:
    # UI
    noteSize: int = 100
    lineWidth: int = 120
    lineStart: int = 0
    noteSpawnPosition: int = -50
    hitPosition: int = 900
    judgementPosition: int = 500
    comboPosition: int = 300
    noteColor: Sequence[int]
    # Key Bind
    keyBindDict: Dict[int, List[int]] = {}
    # judgementTextSpriteDict: Dict[str, JudgementTextSprite] = {}
    # variableTextList: Dict[str, VariableTextSprite] = {}  # 用于监控数值变化后调用对应sprite的update更新view