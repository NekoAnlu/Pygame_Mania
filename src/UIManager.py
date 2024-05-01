import pygame
import pygame_gui
from pygame import Surface
from pygame_gui.elements import *

from src.Model.GameModel import GameModel
from src.Model.SettingModel import *
from src.Grahpic.ManiaSprite import *


class UIManager:
    def __init__(self, game_model: GameModel, level_model, player_model, game_setting, pygame_clock):
        self.uiManager = pygame_gui.UIManager((1920, 1080))

        # 字体
        self.uiManager.add_font_paths('Silver', '../font/Silver.ttf')
        self.uiManager.print_unused_fonts()
        self.uiManager.preload_fonts([{'name': 'Silver', 'point_size': 14, 'style': 'regular'}])

        # 主题(要在读字体后)
        self.uiManager.get_theme().load_theme('UITheme/Test.json')

        # 数据模型
        self.uiModel = ManiaUIModel()
        self.levelModel = level_model
        self.playerModel = player_model
        self.gameModel = game_model
        self.gameSetting = game_setting
        self.pygameClock = pygame_clock
        self.deltaTime = self.pygameClock.tick(1000) / 1000

        # GUI对象列表
        self.titleUIDict = {}
        self.judgementLabelDict = {}
        self.variableLabelDict = {}

        # 标题song下拉菜单选项字典
        self.songDropDownMenuDict = {}
        self.chartDropDownMenuDict = {}

        # 个别用draw画的美术资源仍然需要精灵组
        self.gameSpriteGroup = pygame.sprite.Group()

        # 初始化
        # self.init_ui()
        self.init_ui_event()

    def load_cover(self) -> Surface:
        _image: Surface
        _size = (640, 360)
        if self.gameModel.selectedChart is not None:
            _image = pygame.image.load(self.gameModel.selectedChart.backgroundPath).convert()

            # 保持长宽比放大图片 长宽自适应
            if _image.get_width() > _image.get_height():
                _scaleFactor = _size[1] / _image.get_height()
            else:
                _scaleFactor = _size[0] / _image.get_width()

            _image = pygame.transform.smoothscale(_image,
                                                  ((_image.get_width() * _scaleFactor), _image.get_height() * _scaleFactor))

            _image = _image.subsurface((0, 0), _size)

            # 居中
            #_image.get_rect(center=(self.gameSetting.screenWidth / 2, self.gameSetting.screenHeight / 2))

            # 叠暗化
            _darkImage = pygame.Surface(_size)
            _darkImage.fill((0, 0, 0))
            _darkImage.set_alpha(50)  # 调整暗化程度位置

            # 直接预处理叠上
            pygame.surface.Surface.blit(_image, _darkImage, (0, 0))

        else:
            _image = pygame.Surface(_size).convert()
            pygame.draw.rect(_image, (0, 0, 0), ((0, 0), _size), 10, 30)

        return _image

    # ------------------------- 标题UI -----------------------------
    def init_title_ui(self):
        # self.uiManager.clear_and_reset()
        _TitleText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((100, 300), (800, 500)),
            text='PyMania',
            manager=self.uiManager,
            object_id='#Title_Text')

        _SongCoverImage = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((1060, 100), (640, 360)),
            image_surface=self.load_cover(),
            manager=self.uiManager)

        _SongSelectDropDownMenu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect((1200, 600), (500, 50)),
            options_list=['Select Music......'],
            starting_option='Select Music......',
            manager=self.uiManager,
            object_id='#SongSelectDropDownMenu')
        _SongSelectDropDownMenuLabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-300, 10), (300, 80)),
            text='Select Music : ',
            manager=self.uiManager,
            object_id='#Label_Text',
            anchors={'right': 'right', 'right_target': _SongSelectDropDownMenu,
                     'centery': 'centery', 'centery_target': _SongSelectDropDownMenu})

        _ChartSelectDropDownMenu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect((1200, 680), (500, 50)),
            options_list=['......'],
            starting_option=".......",
            manager=self.uiManager,
            object_id='#SongSelectDropDownMenu')
        _ChartSelectDropDownMenuLabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-300, 10), (300, 80)),
            text='Select Chart : ',
            manager=self.uiManager,
            object_id='#Label_Text',
            anchors={'right': 'right', 'right_target': _ChartSelectDropDownMenu,
                     'centery': 'centery', 'centery_target': _ChartSelectDropDownMenu})

        _DropSpeedSlider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((1200, 760), (500, 50)),
            start_value=20,
            value_range=(10, 40),
            manager=self.uiManager,
            object_id='#DropSpeedSlider')
        _DropSpeedSliderLabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-300, 10), (300, 80)),
            text='Drop Speed : ',
            manager=self.uiManager,
            object_id='#Label_Text',
            anchors={'right': 'right', 'right_target': _DropSpeedSlider,
                     'centery': 'centery', 'centery_target': _DropSpeedSlider})

        _ODSlider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((1200, 840), (500, 50)),
            start_value=8,
            value_range=(0, 10),
            manager=self.uiManager,
            object_id='#DropSpeedSlider')
        _ODSliderLabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-300, 10), (300, 80)),
            text='OD : ',
            manager=self.uiManager,
            object_id='#Label_Text',
            anchors={'right': 'right', 'right_target': _ODSlider,
                     'centery': 'centery', 'centery_target': _ODSlider})

        _GameStartButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((1500, 920), (200, 100)),
            text='Start',
            manager=self.uiManager,
            object_id='#GameStartButton')

        _ChartSelectDropDownMenu.disable()

        self.titleUIDict["TitleText"] = _TitleText
        self.titleUIDict["SongCoverImage"] = _SongCoverImage
        self.titleUIDict["SongSelectDropDownMenu"] = _SongSelectDropDownMenu
        self.titleUIDict["SongSelectDropDownMenuLabel"] = _SongSelectDropDownMenuLabel
        self.titleUIDict["ChartSelectDropDownMenu"] = _ChartSelectDropDownMenu
        self.titleUIDict["ChartSelectDropDownMenuLabel"] = _ChartSelectDropDownMenu
        self.titleUIDict["DropSpeedSlider"] = _DropSpeedSlider
        self.titleUIDict["DropSpeedSliderLabel"] = _DropSpeedSlider
        self.titleUIDict["ODSlider"] = _ODSlider
        self.titleUIDict["ODSliderLabel"] = _ODSlider
        self.titleUIDict["GameStartButton"] = _GameStartButton

    def fill_title_dropdown_menu(self):
        _songSelectDropDownMenu = self.titleUIDict['SongSelectDropDownMenu']

        _songOptions = []
        for song in self.gameModel.songDict.values():
            if len(song.charts) > 0:
                _songOptions.append(song.artist + ' - ' + song.title)
                self.songDropDownMenuDict[song.artist + ' - ' + song.title] = song

        _songSelectDropDownMenu.add_options(_songOptions)

    # 游戏UI
    def init_game_ui(self):
        self.uiModel.lineStart = self.gameSetting.screenWidth / 2 - self.uiModel.lineWidth * len(
            self.levelModel.noteList) / 2.5
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

        # 计数信息
        _PPerfectCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 700), (150, 100)),
            text='Perfect: ',
            manager=self.uiManager,
            object_id='##PPerfectCount_Text')
        _PerfectCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 730), (150, 100)),
            text='Perfect: ',
            manager=self.uiManager,
            object_id='##PerfectCount_Text')
        _GreatCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 760), (150, 100)),
            text='Great: ',
            manager=self.uiManager,
            object_id='##GreatCount_Text')
        _CoolCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 790), (150, 100)),
            text='Cool: ',
            manager=self.uiManager,
            object_id='##CoolCount_Text')
        _BadCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 820), (150, 100)),
            text='Bad: ',
            manager=self.uiManager,
            object_id='##BadCount_Text')
        _MissCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 850), (150, 100)),
            text='Miss: ',
            manager=self.uiManager,
            object_id='##MissCount_Text')

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

        self.variableLabelDict['PPerfectCount'] = _PPerfectCountText
        self.variableLabelDict['PerfectCount'] = _PerfectCountText
        self.variableLabelDict['GreatCount'] = _GreatCountText
        self.variableLabelDict['CoolCount'] = _CoolCountText
        self.variableLabelDict['BadCount'] = _BadCountText
        self.variableLabelDict['MissCount'] = _MissCountText

    # ------------------------- UI Event -------------------------------
    def init_ui_event(self):
        _uiEventIndex = pygame.USEREVENT + 32

        self.JUDGEMENT_HIDE_EVENT = _uiEventIndex + 1

    def process_ui_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.type == self.JUDGEMENT_HIDE_EVENT:
                self.hide_judgement_text()
            # 下拉菜单变更事件
            elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                # 切换选曲触发 更新谱面列表
                if event.ui_element == self.titleUIDict['SongSelectDropDownMenu']:
                    self.update_title_chart_dropdown(event.text)
                    self.titleUIDict['ChartSelectDropDownMenu'].enable()
                    self.titleUIDict["SongCoverImage"].image = self.load_cover()
                # 更新当前所选chart
                elif event.ui_element == self.titleUIDict['ChartSelectDropDownMenu']:
                    self.gameModel.selectedChart = self.chartDropDownMenuDict[event.text]
            # UI按钮按下事件
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.titleUIDict['GameStartButton']:
                    if self.gameModel.selectedChart is not None:
                        # 触发切换loop
                        self.gameModel.gameLoop = 'Game'
                        self.kill_title_ui()
            # 滑条滑动事件
            elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.titleUIDict['DropSpeedSlider']:
                    self.gameSetting.noteSpeed = event.value
                elif event.ui_element == self.titleUIDict['ODSlider']:
                    self.gameSetting.OD = event.value
                    self.gameSetting.cal_judgement_timing()
        self.uiManager.process_events(event)

    # 定时隐藏判定信息事件
    def hide_judgement_text(self):
        for _label in self.judgementLabelDict.values():
            _label.hide()

    # --------------------- update view ---------------------------------
    def update_ui(self):
        # self.update_variable_text()
        # self.gameSpriteGroup.update()
        self.uiManager.update(self.deltaTime)

    # 选曲后更新选谱下拉框
    def update_title_chart_dropdown(self, item_str):
        _chartSelectDropDownMenu = self.titleUIDict['ChartSelectDropDownMenu']
        _currSong = self.songDropDownMenuDict[item_str]

        # 清空原有字典
        self.chartDropDownMenuDict.clear()

        _chartOptions = []
        for chart in _currSong.charts:
            _chartOptions.append(chart.version)
            self.chartDropDownMenuDict[chart.version] = chart

        # 创建一个新的下拉框
        _new_chartSelectDropDownMenu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=_chartSelectDropDownMenu.get_rect(),
            options_list=_chartOptions,
            starting_option=_chartOptions[0],
            manager=self.uiManager,
            object_id='#SongSelectDropDownMenu')

        # 杀掉老的下拉框
        _chartSelectDropDownMenu.kill()

        # 更新所选chart
        self.gameModel.selectedChart = _currSong.charts[0]
        self.titleUIDict['ChartSelectDropDownMenu'] = _new_chartSelectDropDownMenu

    # 判定信息UI更新 在控制器调用
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

        self.variableLabelDict['PPerfectCount'].set_text(f"{'Perfect: '} {self.playerModel.pPerfectCount:>{5}}")
        self.variableLabelDict['PerfectCount'].set_text(f"{'Perfect: '} {self.playerModel.perfectCount:>{5}}")
        self.variableLabelDict['GreatCount'].set_text(f"{'Great: '} {self.playerModel.greatCount:>{5}}")
        self.variableLabelDict['CoolCount'].set_text(f"{'Cool: '} {self.playerModel.coolCount:>{5}}")
        self.variableLabelDict['BadCount'].set_text(f"{'Bad: '} {self.playerModel.badCount:>{5}}")
        self.variableLabelDict['MissCount'].set_text(f"{'Miss: '} {self.playerModel.missCount:>{5}}")

        self.variableLabelDict['Fps'].set_text(str(round(self.pygameClock.get_fps())))

    # 用于清理UI
    def kill_title_ui(self):
        for ui in self.titleUIDict.values():
            ui.kill()

    # ----------------------- draw -------------------------------
    def draw_front_ui(self, screen):
        self.uiManager.draw_ui(screen)

    def draw_back_ui(self, screen):
        self.gameSpriteGroup.draw(screen)
