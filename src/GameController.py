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

        self.gameSetting.deltaTime = self.pygameClock.tick(120)

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
        _image = pygame.image.load(self.levelModel.currentChart.backgroundPath)

        # 保持长宽比放大图片 长宽自适应
        if _image.get_width() > _image.get_height():
            _scaleFactor = 1080 / float(_image.get_height())
        else:
            _scaleFactor = 1920 / float(_image.get_width())

        _image = pygame.transform.smoothscale(_image,
                                              (_image.get_height() * _scaleFactor, _image.get_width() * _scaleFactor))

        # 居中
        _image.get_rect(center=(1920 / 2, 1080 / 2))

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

    def init_ui(self):
        # data
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
        _ComboText = VariableTextSprite('0', 70, (0, 255, 255), (_panelCenterX, self.uiModel.comboPosition))
        self.variableTextGroup.add(_ComboText)
        self.uiModel.variableTextList['Combo'] = _ComboText

    def play_music(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

    def spawn_notes(self):
        _currTime = self.levelModel.timer
        _dropTime = ((self.uiModel.noteDestination - self.uiModel.noteSpawnPosition) / self.levelModel.noteSpeed) * 1000

        for i, lineIndex in enumerate(self.lineIndex):
            while self.lineIndex[i] < len(self.levelModel.noteList[i]) and self.levelModel.noteList[i][self.lineIndex[i]].startTiming <= _currTime + _dropTime:
                _x = self.uiModel.lineStart + self.uiModel.lineWidth * i
                # print(self.levelModel.noteList[i][self.lineIndex[i]].noteType == 0)
                if self.levelModel.noteList[i][self.lineIndex[i]].noteType == 0:
                    _noteObj = self.levelModel.noteSpritePool.get_note((_x, self.uiModel.noteSpawnPosition), (_x, self.uiModel.noteDestination),self.levelModel.noteList[i][self.lineIndex[i]].startTiming)
                    self.levelModel.noteQueue[i].append(_noteObj)
                else:
                    _noteObj = self.levelModel.lnSpritePool.get_note((_x, self.uiModel.noteSpawnPosition), (_x, self.uiModel.noteDestination), self.levelModel.noteList[i][self.lineIndex[i]].startTiming, self.levelModel.noteList[i][self.lineIndex[i]].endTiming)
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

        # self.judgementTextGroup.update()
        # self.judgementTextGroup.draw(screen)
        #
        # self.variableTextGroup.draw(screen)

    # note图层之上的UI
    def draw_front_ui(self, screen):
        self.judgementTextGroup.update()
        self.judgementTextGroup.draw(screen)

        self.variableTextGroup.draw(screen)

    def game_start(self, screen):
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

            # LN尾判定无保护
            if is_key_up and _note.noteType == 1 and _note.isHolding:
                self.note_judgement(_offset)
                _note.isHolding = False
                # _note.active = False
                self.levelModel.noteQueue[line_index].pop(0)
                return

            # 是否在可判定区间内
            if _offset <= self.gameSetting.timing_Miss:
                self.note_judgement(_offset)
                if _note.noteType == 1 and not _note.isHolding:
                    _note.isHolding = True
                else:
                    # 如果是普通按键直接回收并隐藏
                    _note.active = False
                    self.levelModel.noteQueue[line_index].pop(0)

    def note_judgement(self, _offset):
        if _offset <= self.gameSetting.timing_Bad:
            if _offset <= self.gameSetting.timing_PPerfect:
                self.update_judgement_text('PPerfect')
            elif _offset <= self.gameSetting.timing_Perfect:
                self.update_judgement_text('Perfect')
            elif _offset <= self.gameSetting.timing_Great:
                self.update_judgement_text('Great')
            elif _offset <= self.gameSetting.timing_Cool:
                self.update_judgement_text('Cool')
            else:
                self.update_judgement_text('Bad')
            self.playerModel.combo += 1
        else:
            self.update_judgement_text('Miss')
            self.playerModel.combo = 0

    # 每次update更新队列里所有miss的note
    def update_note_queue(self):
        for i in range(len(self.levelModel.noteQueue)):
            while len(self.levelModel.noteQueue[i]) > 0 and not self.levelModel.noteQueue[i][0].active:
                self.levelModel.noteQueue[i].pop(0)
                self.update_judgement_text('Miss')
                self.playerModel.combo = 0
            # LN头判定
            for j in range(len(self.levelModel.noteQueue[i])):
                if len(self.levelModel.noteQueue[i]) > 0 and self.levelModel.noteQueue[i][j].noteType == 1 and self.levelModel.noteQueue[i][j].isHeadMiss:
                    self.update_judgement_text('Miss')
                    self.playerModel.combo = 0

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

    # ---------------------事件处理-----------------------------
    def on_key_press_event(self, key_event):
        self.uiSpritesGroup.update(key_event)
        self.hit_note_event(key_event)

# game = ManiaGame()
# game.test()
