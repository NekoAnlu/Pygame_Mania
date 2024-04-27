from math import sqrt

import pygame
from pygame import *
from pygame.locals import *

from Model.GameModel import *
from Model.SettingModel import *
from Converter import *
from src.Grahpic.ManiaSprite import *


class ManiaGame:
    lineIndex: List[int] = []
    leadInTime: int = 2000

    def __init__(self):
        # 初始化数据模型
        self.levelModel = LevelModel()
        self.uiModel = ManiaUIModel()
        self.gameSetting = GameSetting()
        self.playerModel = PlayerModel()

        # pygame相关
        pygame.mixer.init()

        self.noteSpritesGroup = pygame.sprite.Group()
        self.judgementTextGroup = pygame.sprite.Group()
        self.uiSpritesGroup = pygame.sprite.Group()
        self.variableTextGroup = pygame.sprite.Group()

        self.pygameClock = pygame.time.Clock()

        # self.gameSetting.deltaTime = self.pygameClock.tick(120)

    def load_resource(self):
        # 读谱面
        converter = MCConverter()
        self.levelModel.currentSong = converter.mc_converter('1')
        self.levelModel.currentChart = self.levelModel.currentSong.charts[0]

        # 读和处理各种资源
        self.preprocess_notes()

        pygame.mixer.music.load(self.levelModel.currentChart.audioPath)
        self.load_background_image()

        # 初始化UI
        self.init_ui()

    def load_background_image(self):
        _image = pygame.image.load(self.levelModel.currentChart.backgroundPath).convert()

        # 保持长宽比放大图片 长宽自适应
        if _image.get_width() > _image.get_height():
            _scaleFactor = self.gameSetting.screenHeight / _image.get_height()
        else:
            _scaleFactor = self.gameSetting.screenWidth / _image.get_width()

        _image = pygame.transform.smoothscale(_image,
                                              ((_image.get_width() * _scaleFactor), _image.get_height() * _scaleFactor))

        # 居中
        _image.get_rect(center=(self.gameSetting.screenWidth / 2, self.gameSetting.screenHeight / 2))

        # 叠暗化
        _darkImage = pygame.Surface(_image.get_size())
        _darkImage.fill((0, 0, 0))
        _darkImage.set_alpha(230)  # 调整暗化程度位置

        # 直接预处理叠上
        pygame.surface.Surface.blit(_image, _darkImage, (0, 0))

        self.levelModel.backgroundImage = _image

    # 把note按轨道位置分为4个队列
    def preprocess_notes(self):
        for _note in self.levelModel.currentChart.noteList:
            _lineIndex = _note.line
            # 动态判断谱面key数初始化对应数量的队列和列表
            while len(self.levelModel.noteList) <= _lineIndex:
                self.levelModel.noteList.append([])
                self.levelModel.noteQueue.append([])
                self.lineIndex.append(0)
            self.levelModel.noteList[_lineIndex].append(_note)
            # new 计算按键总数 LN算2note
            self.levelModel.totalNotes += 1 if _note.noteType == 0 else 2

        # print(self.levelModel.totalNotes)

    def init_ui(self):
        # data
        self.uiModel.lineStart = self.gameSetting.screenWidth / 2 - self.uiModel.lineWidth * len(self.levelModel.noteList) / 2.5

        _panelCenterX = self.uiModel.lineStart + (self.uiModel.lineWidth * (len(self.levelModel.noteList) / 2 - 0.5))


        # ManiaPanel
        _maniaPanel = ManiaPanelSprite(
            (self.uiModel.lineStart + (self.uiModel.lineWidth * (len(self.levelModel.noteList) / 2 - 0.5)), 0),
            self.uiModel.lineWidth * len(self.levelModel.noteList) * 1.1)
        self.uiSpritesGroup.add(_maniaPanel)

        # HitPosition
        for i in range(len(self.levelModel.noteList)):
            _lineSprite = HitPositionSprite(
                (self.uiModel.lineStart + self.uiModel.lineWidth * i, self.uiModel.noteDestination), i)
            self.uiSpritesGroup.add(_lineSprite)

        # Judgement Text (优化！！)
        _PPerfectText = JudgementTextSprite('Perfect', 50, (255, 255, 0),
                                            (_panelCenterX, self.uiModel.judgementPosition))
        _PerfectText = JudgementTextSprite('Perfect', 50, (0, 255, 255),
                                           (_panelCenterX, self.uiModel.judgementPosition))
        _GreatText = JudgementTextSprite('Great', 50, (0, 255, 255), (_panelCenterX, self.uiModel.judgementPosition))
        _CoolText = JudgementTextSprite('Cool', 50, (0, 255, 255), (_panelCenterX, self.uiModel.judgementPosition))
        _BadText = JudgementTextSprite('Bad', 50, (0, 255, 255), (_panelCenterX, self.uiModel.judgementPosition))
        _MissText = JudgementTextSprite('Miss', 50, (255, 0, 0), (_panelCenterX, self.uiModel.judgementPosition))
        self.uiModel.judgementTextSpriteDict['PPerfect'] = _PPerfectText
        self.uiModel.judgementTextSpriteDict['Perfect'] = _PerfectText
        self.uiModel.judgementTextSpriteDict['Great'] = _GreatText
        self.uiModel.judgementTextSpriteDict['Cool'] = _CoolText
        self.uiModel.judgementTextSpriteDict['Bad'] = _BadText
        self.uiModel.judgementTextSpriteDict['Miss'] = _MissText
        self.judgementTextGroup.add(_PPerfectText, _PerfectText, _GreatText, _CoolText, _BadText, _MissText)

        # 变化数值Text
        _ComboText = VariableTextSprite('', 70, (0, 255, 255), (_panelCenterX, self.uiModel.comboPosition), 'center')
        _AccuracyText = VariableTextSprite('', 70, (0, 255, 255), (self.gameSetting.screenWidth, 120), 'right')
        _ScoreText = VariableTextSprite('', 120, (0, 255, 255), (self.gameSetting.screenWidth, 60), 'right')

        _PPerfectCountText = VariableTextSprite('Perfect: ', 30, (255, 255, 0), (30, 700), 'left')
        _PerfectCountText = VariableTextSprite('Perfect: ', 30, (0, 255, 255), (30, 730), 'left')
        _GreatCountText = VariableTextSprite('Great: ', 30, (0, 255, 255), (30, 760), 'left')
        _CoolCountText = VariableTextSprite('Cool: ', 30, (0, 255, 255), (30, 790), 'left')
        _BadCountText = VariableTextSprite('Bad: ', 30, (0, 255, 255), (30, 820), 'left')
        _MissCountText = VariableTextSprite('Miss: ', 30, (0, 255, 255), (30, 850), 'left')

        _FpsText = VariableTextSprite('', 40, (0, 255, 255), (self.gameSetting.screenWidth - 10, self.gameSetting.screenHeight - 50), 'right')

        self.variableTextGroup.add(_ComboText, _AccuracyText, _ScoreText, _FpsText)
        self.variableTextGroup.add(_PPerfectCountText, _PerfectCountText, _GreatCountText, _CoolCountText, _BadCountText, _MissCountText)
        self.uiModel.variableTextList['Combo'] = _ComboText
        self.uiModel.variableTextList['Accuracy'] = _AccuracyText
        self.uiModel.variableTextList['Score'] = _ScoreText
        self.uiModel.variableTextList['Fps'] = _FpsText

        self.uiModel.variableTextList['PPerfectCount'] = _PPerfectCountText
        self.uiModel.variableTextList['PerfectCount'] = _PerfectCountText
        self.uiModel.variableTextList['GreatCount'] = _GreatCountText
        self.uiModel.variableTextList['CoolCount'] = _CoolCountText
        self.uiModel.variableTextList['BadCount'] = _BadCountText
        self.uiModel.variableTextList['MissCount'] = _MissCountText

    def play_music(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        if self.is_game_end():
            pygame.mixer.music.stop()

    def is_game_end(self) -> bool:
        for i in range(len(self.lineIndex)):
            if self.lineIndex[i] < len(self.levelModel.noteList[i]):
                return False
        return True

    def spawn_notes(self):
        _currTime = self.levelModel.timer
        _dropTime = ((self.uiModel.noteDestination - self.uiModel.noteSpawnPosition) / self.levelModel.noteSpeed) * 1000

        for i, lineIndex in enumerate(self.lineIndex):
            while self.lineIndex[i] < len(self.levelModel.noteList[i]) and self.levelModel.noteList[i][self.lineIndex[i]].startTiming <= _currTime + _dropTime:
                _x = self.uiModel.lineStart + self.uiModel.lineWidth * i
                # print(self.levelModel.noteList[i][self.lineIndex[i]].noteType == 0)
                if self.levelModel.noteList[i][self.lineIndex[i]].noteType == 0:
                    _noteObj = self.levelModel.noteSpritePool.get_note((_x, self.uiModel.noteSpawnPosition),
                                                                       (_x, self.uiModel.noteDestination),
                                                                       self.levelModel.noteList[i][
                                                                           self.lineIndex[i]].startTiming)
                    self.levelModel.noteQueue[i].append(_noteObj)
                else:
                    _noteObj = self.levelModel.lnSpritePool.get_note((_x, self.uiModel.noteSpawnPosition),
                                                                     (_x, self.uiModel.noteDestination),
                                                                     self.levelModel.noteList[i][
                                                                         self.lineIndex[i]].startTiming,
                                                                     self.levelModel.noteList[i][
                                                                         self.lineIndex[i]].endTiming)
                    self.levelModel.noteQueue[i].append(_noteObj)

                self.lineIndex[i] += 1

    # 画按键的更新方法
    def draw_notes(self, screen):
        self.levelModel.noteSpritePool.add_to_group(self.noteSpritesGroup)
        self.levelModel.lnSpritePool.add_to_group(self.noteSpritesGroup)
        self.noteSpritesGroup.update(self.levelModel.noteSpeed, self.levelModel.timer)
        self.noteSpritesGroup.draw(screen)

    def draw_background_ui(self, screen):
        screen.blit(self.levelModel.backgroundImage, self.levelModel.backgroundImage.get_rect())
        self.uiSpritesGroup.draw(screen)

    # note图层之上的UI
    def draw_front_ui(self, screen):
        self.judgementTextGroup.update()
        self.judgementTextGroup.draw(screen)

        self.variableTextGroup.draw(screen)

    # --------------------判定相关 UI 逻辑-------------------------
    def hit_note_event(self, key_event):
        if key_event.type == pygame.KEYDOWN:
            if key_event.key == pygame.K_d:
                self.on_hit_note(0, self.levelModel.timer, False)
            elif key_event.key == pygame.K_f:
                self.on_hit_note(1, self.levelModel.timer, False)
            elif key_event.key == pygame.K_j:
                self.on_hit_note(2, self.levelModel.timer, False)
            elif key_event.key == pygame.K_k:
                self.on_hit_note(3, self.levelModel.timer, False)
        if key_event.type == pygame.KEYUP:
            if key_event.key == pygame.K_d:
                self.on_hit_note(0, self.levelModel.timer, True)
            elif key_event.key == pygame.K_f:
                self.on_hit_note(1, self.levelModel.timer, True)
            elif key_event.key == pygame.K_j:
                self.on_hit_note(2, self.levelModel.timer, True)
            elif key_event.key == pygame.K_k:
                self.on_hit_note(3, self.levelModel.timer, True)

    def on_hit_note(self, line_index, timing, is_key_up):
        if len(self.levelModel.noteQueue[line_index]) > 0:
            _note = self.levelModel.noteQueue[line_index][0]

            # 防止抬起判定
            if is_key_up and _note.noteType == 0:
                return
            if is_key_up and _note.noteType == 1 and not _note.isHolding:
                return

            # 计算时间差
            if _note.noteType == 1:
                if not _note.isHolding:
                    _offset = abs(_note.timing - timing)
                else:
                    _offset = abs(_note.endTiming - timing)
            else:
                _offset = abs(_note.timing - timing)

            # LN判定范围更小 且miss单独处理（可优化？）
            if _note.noteType == 1:
                # 如果松LN后再按下判定滑条尾
                if not is_key_up and _note.isHeadMiss and not _note.isHolding:
                    _note.isHolding = True
                # 正常按下判定
                elif _offset <= self.gameSetting.timing_Bad:
                    self.timing_judgement(_offset, _note)
                    # LN正常按下
                    if not _note.isHolding:
                        _note.isHolding = True
                    # LN尾巴判定且没有提前松手
                    elif is_key_up and _note.isHolding:
                        _note.isHolding = False
                        _note.active = False
                        self.levelModel.noteQueue[line_index].pop(0)
                # 判定保护miss判定
                elif _offset <= self.gameSetting.timing_Miss:
                    # LN头直接miss
                    if not _note.isHolding:
                        _note.isHeadMiss = True
                # 长条尾提前松手判定
                else:
                    # LN提前松手miss
                    if is_key_up and _note.isHolding:
                        _note.isHolding = False
                        _note.isHeadMiss = True
                        _note.canJudge = False

            # 普通按键是否在可判定区间内
            elif _note.noteType == 0 and _offset <= self.gameSetting.timing_Miss:
                # 基础判定
                self.timing_judgement(_offset, _note)
                # 如果是普通按键直接回收并隐藏
                _note.active = False
                self.levelModel.noteQueue[line_index].pop(0)

    # 判定信息显示 + 数据更新
    def timing_judgement(self, _offset, _note):
        if _offset <= self.gameSetting.timing_Bad:
            if _offset <= self.gameSetting.timing_PPerfect:
                self.note_judgement('PPerfect')
            elif _offset <= self.gameSetting.timing_Perfect:
                self.note_judgement('Perfect')
            elif _offset <= self.gameSetting.timing_Great:
                self.note_judgement('Great')
            elif _offset <= self.gameSetting.timing_Cool:
                self.note_judgement('Cool')
            else:
                self.note_judgement('Bad')
        else:
            self.note_judgement('Miss')

    # 具体判定对view和model的更新
    def note_judgement(self, judge_name):
        self.update_judgement_text(judge_name)
        if judge_name == 'PPerfect':
            self.playerModel.pPerfectCount += 1
            self.playerModel.combo += 1
        elif judge_name == 'Perfect':
            self.playerModel.perfectCount += 1
            self.playerModel.combo += 1
        elif judge_name == 'Great':
            self.playerModel.greatCount += 1
            self.playerModel.combo += 1
        elif judge_name == 'Cool':
            self.playerModel.coolCount += 1
            self.playerModel.combo += 1
        elif judge_name == 'Bad':
            self.playerModel.badCount += 1
            self.playerModel.combo = 0
        elif judge_name == 'Miss':
            self.playerModel.missCount += 1
            self.playerModel.combo = 0

        # 每次判定时计算一次分数
        self.cal_score(judge_name)
        self.cal_acc()

    # 每次update更新队列里所有miss的note
    def update_note_queue(self):
        for i in range(len(self.levelModel.noteQueue)):
            # 按键回收隐藏
            while len(self.levelModel.noteQueue[i]) > 0 and not self.levelModel.noteQueue[i][0].active:
                self.levelModel.noteQueue[i].pop(0)
                self.note_judgement('Miss')
            # LN头判定
            for j in range(len(self.levelModel.noteQueue[i])):
                if len(self.levelModel.noteQueue[i]) > 0 and self.levelModel.noteQueue[i][j].noteType == 1 and \
                        self.levelModel.noteQueue[i][j].isHeadMiss:
                    self.note_judgement('Miss')
                # # 是否还可以判定（更新判定队列）
                # while not self.levelModel.noteQueue[i][0].canJudge:
                #     self.levelModel.noteQueue[i].pop(0)

    # Acc (osu mania scorev1)
    def cal_acc(self):
        self.playerModel.accuracy = ((300 * (self.playerModel.perfectCount + self.playerModel.pPerfectCount)
                                      + 200 * self.playerModel.greatCount + 100 * self.playerModel.coolCount
                                      + 50 * self.playerModel.badCount)
                                     / (300 * (self.playerModel.perfectCount + self.playerModel.pPerfectCount
                                               + self.playerModel.greatCount + self.playerModel.coolCount
                                               + self.playerModel.badCount + self.playerModel.missCount))) * 100
        # 保留2位小数
        self.playerModel.accuracy = round(self.playerModel.accuracy, 2)

    # Score (osu mania scorev1)
    # https://osu.ppy.sh/wiki/zh/Gameplay/Score/ScoreV1/osu%21mania
    def cal_score(self, judge_name):
        # 计算用基础值
        _HitValue = 0
        _HitBonusValue = 0
        _HitBonus = 0
        _HitPunishment = 0

        if judge_name == 'PPerfect':
            _HitValue = 320
            _HitBonusValue = 32
            _HitBonus = 2
        elif judge_name == 'Perfect':
            _HitValue = 300
            _HitBonusValue = 32
            _HitBonus = 1
        elif judge_name == 'Great':
            _HitValue = 200
            _HitBonusValue = 16
            _HitPunishment = 8
        elif judge_name == 'Cool':
            _HitValue = 100
            _HitBonusValue = 8
            _HitPunishment = 24
        elif judge_name == 'Bad':
            _HitValue = 50
            _HitBonusValue = 4
            _HitPunishment = 44
        elif judge_name == 'miss':
            _HitValue = 0
            _HitBonusValue = 0
            _HitPunishment = 100

        _MaxScore = 1000000

        _Bonus = self.playerModel.scoreBonus + _HitBonus - _HitPunishment
        _Bonus = min(100, _Bonus)
        _Bonus = max(0, _Bonus)
        self.playerModel.scoreBonus = _Bonus

        _BaseScore = (_MaxScore * 0.5 / self.levelModel.totalNotes) * (_HitValue / 320.0)
        _BonusScore = (_MaxScore * 0.5 / self.levelModel.totalNotes) * (_HitBonusValue * sqrt(_Bonus) / 320.0)

        self.playerModel.score += int(_BaseScore + _BonusScore)

    # ------------------- UI更新 ---------------------------

    def update_judgement_text(self, text):
        for _sprite in self.uiModel.judgementTextSpriteDict.values():
            _sprite.active = False
            self.judgementTextGroup.remove(_sprite)
        self.uiModel.judgementTextSpriteDict[text].active = True
        self.uiModel.judgementTextSpriteDict[text].timer = 0  # 初始化timer
        self.judgementTextGroup.add(self.uiModel.judgementTextSpriteDict[text])

    # 可优化？
    def update_variable_text(self):
        self.uiModel.variableTextList['Combo'].update(self.playerModel.combo)
        self.uiModel.variableTextList['Accuracy'].update(str(self.playerModel.accuracy) + '%')
        self.uiModel.variableTextList['Score'].update(self.playerModel.score)

        self.uiModel.variableTextList['PPerfectCount'].update(self.playerModel.pPerfectCount)
        self.uiModel.variableTextList['PerfectCount'].update(self.playerModel.perfectCount)
        self.uiModel.variableTextList['GreatCount'].update(self.playerModel.greatCount)
        self.uiModel.variableTextList['CoolCount'].update(self.playerModel.coolCount)
        self.uiModel.variableTextList['BadCount'].update(self.playerModel.badCount)
        self.uiModel.variableTextList['MissCount'].update(self.playerModel.missCount)

        self.uiModel.variableTextList['Fps'].update(round(self.pygameClock.get_fps()))

    # ---------------------事件处理-----------------------------
    def on_key_press_event(self, key_event):
        self.uiSpritesGroup.update(key_event)
        self.hit_note_event(key_event)

    # ------------------------------ 主循环 ------------------------
    def game_start(self, screen):
        # 每帧调用设置fps
        self.gameSetting.deltaTime = self.pygameClock.tick(1000)

        # 更新Timer
        self.levelModel.timer = pygame.mixer.music.get_pos() - self.leadInTime

        # 清空之前的group(在修改group内变量前清空避免报错
        self.noteSpritesGroup.empty()

        # 一些数据更新
        self.update_note_queue()
        self.update_variable_text()

        # 生成按键精灵
        self.spawn_notes()

        # 渲染 (注意图层)
        self.draw_background_ui(screen)
        self.draw_notes(screen)
        self.draw_front_ui(screen)

        # Lead In
        self.leadInTime -= self.gameSetting.deltaTime
        if self.leadInTime <= 0:
            self.play_music()
            self.leadInTime = 0

        pygame.display.update()

# game = ManiaGame()
# game.test()
