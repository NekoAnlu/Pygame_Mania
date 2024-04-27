# 游戏相关设置
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
