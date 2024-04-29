import pygame
import pygame_gui
from src.Model.SettingModel import *
from src.Grahpic.ManiaSprite import *

class UIManager:
    def __init__(self, level_model, player_model, pygame_clock):
        self.uiManager = pygame_gui.UIManager((1920, 1080))

        # 字体
        self.uiManager.add_font_paths('Silver', '../font/Silver.ttf')
        self.uiManager.print_unused_fonts()
        self.uiManager.preload_fonts([{'name': 'Silver', 'point_size': 14, 'style': 'regular'}])

        # 主题(要在读字体后)
        self.uiManager.get_theme().load_theme('UITheme/Test.json')

        self.levelModel = level_model
        self.playerModel = player_model
        # 静态
        self.uiModel = ManiaUIModel()
        self.gameSetting = GameSetting()
        self.pygameClock = pygame_clock

        # GUI对象列表
        self.judgementLabelDict = {}
        self.variableLabelDict = {}

        # 个别用draw画的美术资源仍然需要精灵组
        self.gameSpriteGroup = pygame.sprite.Group()

        # 初始化
        # self.init_ui()
        self.init_ui_event()


    def init_ui(self):
        self.uiModel.lineStart = self.gameSetting.screenWidth / 2 - self.uiModel.lineWidth * len(self.levelModel.noteList) / 2.5
        _panelCenterX = self.uiModel.lineStart + (self.uiModel.lineWidth * (len(self.levelModel.noteList) / 2.0 - 0.5))

        # ManiaPanel
        _maniaPanel = ManiaPanelSprite(
            (self.uiModel.lineStart + (self.uiModel.lineWidth * (len(self.levelModel.noteList) / 2.0 - 0.5)), 0),
            self.uiModel.lineWidth * len(self.levelModel.noteList) * 1.1)
        self.gameSpriteGroup.add(_maniaPanel)

        # HitPosition
        for i in range(len(self.levelModel.noteList)):
            _lineSprite = HitPositionSprite(
                (self.uiModel.lineStart + self.uiModel.lineWidth * i, self.uiModel.noteDestination), i)
            self.gameSpriteGroup.add(_lineSprite)

        # 判定信息
        _PPerfectText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.uiModel.judgementPosition), (110, 300)),
            text='Perfect',
            manager=self.uiManager,
            object_id='##PPerfect_Text',
            anchors={'centerx': 'centerx'})
        _PerfectText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.uiModel.judgementPosition), (110, 300)),
            text='Perfect',
            manager=self.uiManager,
            object_id='##Perfect_Text',
            anchors={'centerx': 'centerx'})
        _GreatText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.uiModel.judgementPosition), (100, 300)),
            text='Great',
            manager=self.uiManager,
            object_id='##Great_Text',
            anchors={'centerx': 'centerx'})
        _CoolText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.uiModel.judgementPosition), (100, 300)),
            text='Cool',
            manager=self.uiManager,
            object_id='##Cool_Text',
            anchors={'centerx': 'centerx'})
        _BadText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.uiModel.judgementPosition), (100, 300)),
            text='Bad',
            manager=self.uiManager,
            object_id='##Bad_Text',
            anchors={'centerx': 'centerx'})
        _MissText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.uiModel.judgementPosition), (100, 300)),
            text='Miss',
            manager=self.uiManager,
            object_id='##Miss_Text',
            anchors={'centerx': 'centerx'})
        self.judgementLabelDict['PPerfect'] = _PPerfectText
        self.judgementLabelDict['Perfect'] = _PerfectText
        self.judgementLabelDict['Great'] = _GreatText
        self.judgementLabelDict['Cool'] = _CoolText
        self.judgementLabelDict['Bad'] = _BadText
        self.judgementLabelDict['Miss'] = _MissText
        # 默认隐藏所有判定信息
        self.hide_judgement_text()

        # 变化数值Text
        _ComboText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.uiModel.comboPosition), (100, 100)),
            text='0',
            manager=self.uiManager,
            object_id='#Combo_Text',
            anchors={'centerx': 'centerx'})
        _ScoreText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-510, 0), (500, 120)),
            text='0',
            manager=self.uiManager,
            object_id='#Score_Text',
            anchors={'right': 'right', 'top': 'top'})
        _AccuracyText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-160, 80), (150, 100)),
            text='100.00%',
            manager=self.uiManager,
            object_id='#Accuracy_Text',
            anchors={'right': 'right', 'top': 'top'})
        _FpsText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-55, -55), (50, 50)),
            text='0',
            manager=self.uiManager,
            object_id='#Fps_Text',
            anchors={'right': 'right', 'bottom': 'bottom'})

        self.variableLabelDict['Combo'] = _ComboText
        self.variableLabelDict['Accuracy'] = _AccuracyText
        self.variableLabelDict['Score'] = _ScoreText
        self.variableLabelDict['Fps'] = _FpsText

    #------------------------- UI Event -------------------------------
    def init_ui_event(self):
        _uiEventIndex = pygame.USEREVENT + 32

        self.JUDGEMENT_HIDE_EVENT = _uiEventIndex + 1

    def process_ui_event(self, event):
        self.uiManager.process_events(event)
        if event.type == self.JUDGEMENT_HIDE_EVENT:
            self.hide_judgement_text()

    # 定时隐藏判定信息事件
    def hide_judgement_text(self):
        for _label in self.judgementLabelDict.values():
            _label.hide()

    # --------------------- update view ---------------------------------
    def update_ui(self, delta_time):
        self.update_variable_text()
        # self.gameSpriteGroup.update()
        self.uiManager.update(delta_time)

    # # 判定信息UI更新 在控制器调用
    def update_judgement_text(self, text):
        for _label in self.judgementLabelDict.values():
            _label.hide()
        self.judgementLabelDict[text].show()
        pygame.time.set_timer(self.JUDGEMENT_HIDE_EVENT, 2000)

    # # 更新变化信息 在这里调用
    def update_variable_text(self):
        self.variableLabelDict['Combo'].set_text(str(self.playerModel.combo))
        self.variableLabelDict['Accuracy'].set_text(str(self.playerModel.accuracy) + '%')
        self.variableLabelDict['Score'].set_text(str(self.playerModel.score))
        #
        # self.uiModel.variableTextList['PPerfectCount'].update(self.playerModel.pPerfectCount)
        # self.uiModel.variableTextList['PerfectCount'].update(self.playerModel.perfectCount)
        # self.uiModel.variableTextList['GreatCount'].update(self.playerModel.greatCount)
        # self.uiModel.variableTextList['CoolCount'].update(self.playerModel.coolCount)
        # self.uiModel.variableTextList['BadCount'].update(self.playerModel.badCount)
        # self.uiModel.variableTextList['MissCount'].update(self.playerModel.missCount)
        #
        self.variableLabelDict['Fps'].set_text(str(round(self.pygameClock.get_fps())))

    # ----------------------- draw -------------------------------
    def draw_ui(self, screen):
        self.gameSpriteGroup.draw(screen)
        self.uiManager.draw_ui(screen)