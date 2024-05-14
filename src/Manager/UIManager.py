import math

import pygame
import pygame_gui
from pygame import Surface
from pygame_gui.elements import *

from src.Model.GameModel import GameModel
from src.Model.SettingModel import *
from src.Grahpic.ManiaSprite import *


class UIManager:
    def __init__(self, game_model: GameModel, level_model, player_model, game_setting, mania_setting,  pygame_clock):
        self.uiManager = pygame_gui.UIManager((1920, 1080))

        # 字体
        self.uiManager.add_font_paths('Silver', './font/Silver.ttf')
        self.uiManager.print_unused_fonts()
        self.uiManager.preload_fonts([{'name': 'Silver', 'point_size': 14, 'style': 'regular'}])

        # 主题(要在读字体后)
        self.uiManager.get_theme().load_theme("./src/Manager/ui.json")

        # 数据模型
        self.levelModel = level_model
        self.playerModel = player_model
        self.gameModel = game_model
        self.gameSetting = game_setting
        self.pygameClock = pygame_clock
        self.maniaSetting = mania_setting
        self.deltaTime = self.pygameClock.tick(1000) / 1000

        # GUI对象列表
        self.titleUIDict = {}
        self.judgementLabelDict = {}
        self.variableLabelDict = {}
        self.scoreUIDict = {}

        # 标题song下拉菜单选项字典
        self.songDropDownMenuDict = {}
        self.chartDropDownMenuDict = {}

        # 个别用draw画的美术资源仍然需要精灵组
        self.gameSpriteGroup = pygame.sprite.Group()

        # 初始化
        # self.init_ui()
        self.init_ui_event()

    # 开局和结算都用的上
    def load_cover(self, size, alpha) -> Surface:
        _image: Surface
        if self.gameModel.selectedChart is not None and self.gameModel.selectedChart.backgroundPath != '':
            _image = pygame.image.load(self.gameModel.selectedChart.backgroundPath).convert()

            _resizeRatio = float(size[0]) / size[1]
            _imageRatio = float(_image.get_width()) / _image.get_height()

            # 保持长宽比放大图片 长宽自适应
            if _imageRatio > _resizeRatio:
                _scaleFactor = float(size[1]) / _image.get_height()
            else:
                _scaleFactor = float(size[0]) / _image.get_width()

            _image = pygame.transform.smoothscale(_image,
                                                  ((_image.get_width() * _scaleFactor), _image.get_height() * _scaleFactor))

            _image = _image.subsurface((0, 0), size)

            # 居中
            #_image.get_rect(center=(self.gameSetting.screenWidth / 2, self.gameSetting.screenHeight / 2))

            # 叠暗化
            _darkImage = pygame.Surface(size)
            _darkImage.fill((0, 0, 0))
            _darkImage.set_alpha(alpha)  # 调整暗化程度位置

            # 直接预处理叠上
            pygame.surface.Surface.blit(_image, _darkImage, (0, 0))

        else:
            _image = pygame.Surface(size).convert()
            pygame.draw.rect(_image, (0, 0, 0), ((0, 0), size), 10, 30)

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
            image_surface=self.load_cover((640, 360), 20),
            manager=self.uiManager)

        _SongSelectDropDownMenu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect((1200, 520), (500, 50)),
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
            relative_rect=pygame.Rect((1200, 600), (500, 50)),
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
            relative_rect=pygame.Rect((1200, 680), (500, 50)),
            start_value=self.gameSetting.noteSpeed,
            value_range=(5, 40),
            manager=self.uiManager,
            object_id='#DropSpeedSlider')
        _DropSpeedSliderLabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-300, 10), (300, 80)),
            text='Drop Speed : ',
            manager=self.uiManager,
            object_id='#Label_Text',
            anchors={'right': 'right', 'right_target': _DropSpeedSlider,
                     'centery': 'centery', 'centery_target': _DropSpeedSlider})
        _DropSpeedSliderValue = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 10), (100, 80)),
            text=str(self.gameSetting.noteSpeed),
            manager=self.uiManager,
            object_id='#Value_Text',
            anchors={'left': 'left', 'left_target': _DropSpeedSlider,
                     'centery': 'centery', 'centery_target': _DropSpeedSlider})

        _ODSlider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((1200, 760), (500, 50)),
            start_value=self.gameSetting.OD,
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
        _ODSliderValue = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 10), (100, 80)),
            text=str(self.gameSetting.OD),
            manager=self.uiManager,
            object_id='#Value_Text',
            anchors={'left': 'left', 'left_target': _ODSlider,
                     'centery': 'centery', 'centery_target': _ODSlider})

        _OffsetSlider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((1200, 840), (500, 50)),
            start_value=self.gameSetting.offset,
            value_range=(-100, 100),
            manager=self.uiManager,
            object_id='#DropSpeedSlider')
        _OffsetSliderLabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-300, 10), (300, 80)),
            text='Offset : ',
            manager=self.uiManager,
            object_id='#Label_Text',
            anchors={'right': 'right', 'right_target': _OffsetSlider,
                     'centery': 'centery', 'centery_target': _OffsetSlider})
        _OffsetSliderValue = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 10), (100, 80)),
            text=str(self.gameSetting.offset)+'ms',
            manager=self.uiManager,
            object_id='#Value_Text',
            anchors={'left': 'left', 'left_target': _OffsetSlider,
                     'centery': 'centery', 'centery_target': _OffsetSlider})

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
        self.titleUIDict["ChartSelectDropDownMenuLabel"] = _ChartSelectDropDownMenuLabel
        self.titleUIDict["DropSpeedSlider"] = _DropSpeedSlider
        self.titleUIDict["DropSpeedSliderLabel"] = _DropSpeedSliderLabel
        self.titleUIDict["DropSpeedSliderValue"] = _DropSpeedSliderValue
        self.titleUIDict["ODSlider"] = _ODSlider
        self.titleUIDict["ODSliderLabel"] = _ODSliderLabel
        self.titleUIDict["ODSliderValue"] = _ODSliderValue
        self.titleUIDict["OffsetSlider"] = _OffsetSlider
        self.titleUIDict["OffsetSliderLabel"] = _OffsetSliderLabel
        self.titleUIDict["OffsetSliderValue"] = _OffsetSliderValue
        self.titleUIDict["GameStartButton"] = _GameStartButton

    def fill_title_dropdown_menu(self):
        _songSelectDropDownMenu = self.titleUIDict['SongSelectDropDownMenu']

        _songOptions = []
        for song in self.gameModel.songDict.values():
            if len(song.charts) > 0:
                _songOptions.append(song.artist + ' - ' + song.title)
                self.songDropDownMenuDict[song.artist + ' - ' + song.title] = song

        _songSelectDropDownMenu.add_options(_songOptions)

    # ---------------------------- 游戏UI -----------------------------
    def init_game_ui(self):
        # 背景图
        # _BackgroundImage = pygame_gui.elements.UIImage(
        #     relative_rect=pygame.Rect((0, 0), (1920, 1080)),
        #     image_surface=self.load_cover((1920, 1080), 220),
        #     manager=self.uiManager,
        #     anchors={'center': 'center'})
        # 改为load完直接blit 避免图层问题
        self.levelModel.backgroundImage = self.load_cover((1920, 1080), 210)

        _columnNum = self.levelModel.currentChart.columnNum
        self.maniaSetting.lineStart = self.gameSetting.screenWidth / 2 - self.maniaSetting.lineWidth * (_columnNum / 2.0 - 0.5)
        _panelCenterX = self.maniaSetting.lineStart + (self.maniaSetting.lineWidth * (_columnNum / 2.0 - 0.5))

        # ManiaPanel
        _maniaPanel = ManiaPanelSprite(
            (self.maniaSetting.lineStart + (self.maniaSetting.lineWidth * (_columnNum / 2.0 - 0.5)), 0), self.maniaSetting.lineWidth * _columnNum * 1.05)
        self.gameSpriteGroup.add(_maniaPanel)

        # HitPosition
        for i in range(len(self.levelModel.noteList)):
            _lineSprite = HitPositionSprite(self.maniaSetting.noteSize, self.maniaSetting.noteColor, (self.maniaSetting.lineStart + self.maniaSetting.lineWidth * i, self.maniaSetting.hitPosition), i, self.maniaSetting.keyBindDict)
            self.gameSpriteGroup.add(_lineSprite)

        # 判定信息
        _PPerfectText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.maniaSetting.judgementPosition), (110, 300)),
            text='Perfect',
            manager=self.uiManager,
            object_id='##PPerfect_Text',
            anchors={'centerx': 'centerx'})
        _PerfectText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.maniaSetting.judgementPosition), (110, 300)),
            text='Perfect',
            manager=self.uiManager,
            object_id='##Perfect_Text',
            anchors={'centerx': 'centerx'})
        _GreatText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.maniaSetting.judgementPosition), (100, 300)),
            text='Great',
            manager=self.uiManager,
            object_id='##Great_Text',
            anchors={'centerx': 'centerx'})
        _CoolText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.maniaSetting.judgementPosition), (100, 300)),
            text='Cool',
            manager=self.uiManager,
            object_id='##Cool_Text',
            anchors={'centerx': 'centerx'})
        _BadText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.maniaSetting.judgementPosition), (100, 300)),
            text='Bad',
            manager=self.uiManager,
            object_id='##Bad_Text',
            anchors={'centerx': 'centerx'})
        _MissText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.maniaSetting.judgementPosition), (100, 300)),
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

        # PausePanel
        _PausePanel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (270, 400)),
            starting_height=0,
            manager=self.uiManager,
            object_id='#PausePanel',
            anchors={'center': 'center'})
        _PauseLabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 20), (200, 100)),
            text='Pause',
            manager=self.uiManager,
            object_id='#Combo_Text',
            container=_PausePanel,
            anchors={'centerx': 'centerx'})

        # _ResumeButton = pygame_gui.elements.UIButton(
        #     relative_rect=pygame.Rect((0, 20), (200, 100)),
        #     text='Resume',
        #     manager=self.uiManager,
        #     object_id='#BackButton',
        #     container=_PausePanel,
        #     anchors={'centerx': 'centerx'})
        _RetryButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 120), (200, 100)),
            text='Retry',
            manager=self.uiManager,
            object_id='#BackButton',
            container=_PausePanel,
            anchors={'centerx': 'centerx'})
        _ExitButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 240), (200, 100)),
            text='Exit',
            manager=self.uiManager,
            object_id='#BackButton',
            container=_PausePanel,
            anchors={'centerx': 'centerx'})

        _PausePanel.hide()

        # 变化数值Text
        _ComboText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.maniaSetting.comboPosition), (100, 100)),
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

        # 歌曲信息
        _SongTitleText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((40, 620), (500, 100)),
            text='3333-3333',
            manager=self.uiManager,
            object_id='#IngameInfo_Text')
        _VersionText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((40, 660), (500, 100)),
            text='3333-3333',
            manager=self.uiManager,
            object_id='#IngameInfo_Text')

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
        _FastCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 880), (150, 100)),
            text='Fast: ',
            manager=self.uiManager,
            object_id='##FastCount_Text')
        _LateCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((160, 880), (150, 100)),
            text='Late: ',
            manager=self.uiManager,
            object_id='##LateCount_Text')

        _FpsText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((-55, -55), (50, 50)),
            text='0',
            manager=self.uiManager,
            object_id='#Fps_Text',
            anchors={'right': 'right', 'bottom': 'bottom'})

        # 借助这个dict显隐
        # self.variableLabelDict['BackgroundImage'] = _BackgroundImage
        self.variableLabelDict['PausePanel'] = _PausePanel
        # self.variableLabelDict['ResumeButton'] = _ResumeButton
        self.variableLabelDict['RetryButton'] = _RetryButton
        self.variableLabelDict['ExitButton'] = _ExitButton

        self.variableLabelDict['Combo'] = _ComboText
        self.variableLabelDict['Accuracy'] = _AccuracyText
        self.variableLabelDict['Score'] = _ScoreText
        self.variableLabelDict['Fps'] = _FpsText

        self.variableLabelDict['SongTitleText'] = _SongTitleText
        self.variableLabelDict['VersionText'] = _VersionText

        self.variableLabelDict['PPerfectCount'] = _PPerfectCountText
        self.variableLabelDict['PerfectCount'] = _PerfectCountText
        self.variableLabelDict['GreatCount'] = _GreatCountText
        self.variableLabelDict['CoolCount'] = _CoolCountText
        self.variableLabelDict['BadCount'] = _BadCountText
        self.variableLabelDict['MissCount'] = _MissCountText
        self.variableLabelDict['FastCount'] = _FastCountText
        self.variableLabelDict['LateCount'] = _LateCountText

    # -------------------------- 结算UI ------------------------------
    def init_score_ui(self):
        _BackgroundImage = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((0, 0), (1920, 1080)),
            image_surface=self.load_cover((1920, 1080), 200),
            manager=self.uiManager,
            anchors={'center': 'center'})

        _ScoreLabelText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((600, 50), (600, 800)),
            text='S',
            manager=self.uiManager,
            object_id='#ScoreLabel_Text',
            anchors={'center': 'center'})
        _RetryButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((600, 280), (500, 100)),
            text='Retry',
            manager=self.uiManager,
            object_id='#BackButton',
            anchors={'center': 'center'})
        _BackButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((600, 400), (500, 100)),
            text='Back',
            manager=self.uiManager,
            object_id='#BackButton',
            anchors={'center': 'center'})

        _SongInfoText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 80), (1000, 100)),
            text='Artist - Title',
            manager=self.uiManager,
            object_id='#ScoreSongInfo_Text',
            anchors={'centerx': 'centerx'})
        _SongVersionText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 150), (1000, 100)),
            text='Artist - Lv 31',
            manager=self.uiManager,
            object_id='#SubScoreSongInfo_Text',
            anchors={'centerx': 'centerx'})

        # 具体score
        _ScoreText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((150, 250), (850, 200)),
            text='876543',
            manager=self.uiManager,
            object_id='#Score_Text_In_Score')

        _PPerfectCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((150, 400), (500, 200)),
            text='Perfect: 111',
            manager=self.uiManager,
            object_id='###PPerfectCount_Text')
        _PerfectCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((700, 400), (500, 200)),
            text='Perfect: 222',
            manager=self.uiManager,
            object_id='###PerfectCount_Text')
        _GreatCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((150, 520), (500, 200)),
            text='Great: 333',
            manager=self.uiManager,
            object_id='###GreatCount_Text')
        _CoolCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((700, 520), (500, 200)),
            text='Cool: 44',
            manager=self.uiManager,
            object_id='###CoolCount_Text')
        _BadCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((150, 640), (500, 200)),
            text='Bad: 5',
            manager=self.uiManager,
            object_id='###BadCount_Text')
        _MissCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((700, 640), (500, 200)),
            text='Miss: 6',
            manager=self.uiManager,
            object_id='###MissCount_Text')
        _ComboCountText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((150, 760), (500, 200)),
            text='Combo: 999x',
            manager=self.uiManager,
            object_id='###ComboCount_Text')
        _AccText = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((700, 760), (500, 200)),
            text='Acc: 100.00%',
            manager=self.uiManager,
            object_id='###ComboCount_Text')

        self.scoreUIDict['BackgroundImage'] = _BackgroundImage

        self.scoreUIDict['ScoreLabelText'] = _ScoreLabelText
        self.scoreUIDict['BackButton'] = _BackButton
        self.scoreUIDict['RetryButton'] = _RetryButton

        self.scoreUIDict['ScoreText'] = _ScoreText
        self.scoreUIDict['SongInfoText'] = _SongInfoText
        self.scoreUIDict['SongVersionText'] = _SongVersionText
        self.scoreUIDict['PPerfectCount'] = _PPerfectCountText
        self.scoreUIDict['PerfectCount'] = _PerfectCountText
        self.scoreUIDict['GreatCount'] = _GreatCountText
        self.scoreUIDict['CoolCount'] = _CoolCountText
        self.scoreUIDict['BadCount'] = _BadCountText
        self.scoreUIDict['MissCount'] = _MissCountText
        self.scoreUIDict['ComboCount'] = _ComboCountText
        self.scoreUIDict['Acc'] = _AccText

    def fill_score_page_value(self):
        self.scoreUIDict['ScoreText'].set_text(f"{self.playerModel.score}")
        self.scoreUIDict['SongInfoText'].set_text(self.levelModel.currentSong.artist + " - " + self.levelModel.currentSong.title)
        self.scoreUIDict['SongVersionText'].set_text(self.levelModel.currentChart.version)
        self.scoreUIDict['PPerfectCount'].set_text(f'Perfect: {self.playerModel.pPerfectCount}' )
        self.scoreUIDict['PerfectCount'].set_text(f'Perfect: {self.playerModel.perfectCount}')
        self.scoreUIDict['GreatCount'].set_text(f'Great: {self.playerModel.greatCount}')
        self.scoreUIDict['CoolCount'].set_text(f'Cool: {self.playerModel.coolCount}')
        self.scoreUIDict['BadCount'].set_text(f'Bad: {self.playerModel.badCount}')
        self.scoreUIDict['MissCount'].set_text(f'Miss: {self.playerModel.missCount}')
        self.scoreUIDict['ComboCount'].set_text(f'Combo: {self.playerModel.maxCombo}')
        self.scoreUIDict['Acc'].set_text(f'Acc: {self.playerModel.accuracy}%')

        # 参考osu评分
        if self.playerModel.accuracy >= 100:
            self.scoreUIDict['ScoreLabelText'].set_text('SS')
        elif self.playerModel.accuracy >= 95:
            self.scoreUIDict['ScoreLabelText'].set_text('S')
        elif self.playerModel.accuracy >= 90:
            self.scoreUIDict['ScoreLabelText'].set_text('A')
        elif self.playerModel.accuracy >= 80:
            self.scoreUIDict['ScoreLabelText'].set_text('B')
        elif self.playerModel.accuracy >= 70:
            self.scoreUIDict['ScoreLabelText'].set_text('C')
        else:
            self.scoreUIDict['ScoreLabelText'].set_text('D')

    # ------------------- UI Effect ---------------------------
    # def BounceTextEffect(self):
    #     # 计算一个基于正弦波的跳动效果
    #     bounce_height = 10  # 跳动高度
    #     speed = 2  # 控制跳动的速度
    #     new_y = 250 + math.sin(time_since_start * speed) * bounce_height
    #
    #     # 更新标签位置
    #     label.set_relative_position((350, new_y))


    # ------------------------- UI Event -------------------------------
    def init_ui_event(self):
        _uiEventIndex = pygame.USEREVENT + 32

        self.JUDGEMENT_HIDE_EVENT = _uiEventIndex + 1

    def process_ui_event(self, event):
        # 自动隐藏判定
        if event.type == self.JUDGEMENT_HIDE_EVENT:
            self.hide_judgement_text()
        if event.type == pygame.USEREVENT:
            # 下拉菜单变更事件
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                # 切换选曲触发 更新谱面列表
                if event.ui_element == self.titleUIDict['SongSelectDropDownMenu']:
                    if event.text != 'Select Music......':
                        self.update_title_chart_dropdown(event.text)
                        self.titleUIDict['ChartSelectDropDownMenu'].enable()
                        self.titleUIDict["SongCoverImage"].image = self.load_cover((640, 360), 20)
                    else:
                        self.gameModel.selectedChart = None
                        self.titleUIDict['ChartSelectDropDownMenu'].disable()
                        self.titleUIDict["SongCoverImage"].image = self.load_cover((640, 360), 20)
                # 更新当前所选chart
                elif event.ui_element == self.titleUIDict['ChartSelectDropDownMenu']:
                    self.gameModel.selectedChart = self.chartDropDownMenuDict[event.text]
            # UI按钮按下事件
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                # 标题点击切换loop开始游戏
                if self.gameModel.gameLoop == 'Title':
                    if event.ui_element == self.titleUIDict['GameStartButton']:
                        if self.gameModel.selectedChart is not None:
                            self.gameModel.gameLoop = 'Game'
                # 结算页面
                elif self.gameModel.gameLoop == 'Score':
                    if event.ui_element == self.scoreUIDict['BackButton']:
                        # 避免title cover重复显示
                        self.gameModel.selectedChart = None
                        self.gameModel.gameLoop = 'Title'
                    elif event.ui_element == self.scoreUIDict['RetryButton']:
                        self.gameModel.gameLoop = 'Game'
                # 游戏页面暂停
                elif self.gameModel.gameLoop == 'Game':
                    # if event.ui_element == self.variableLabelDict['ResumeButton']:
                    #     self.gameModel.isGamePause = False
                    if event.ui_element == self.variableLabelDict['RetryButton']:
                        # 偷懒用重开方法
                        self.gameModel.isGamePause = False
                        self.gameModel.gameLoop = 'GameRetry'
                    elif event.ui_element == self.variableLabelDict['ExitButton']:
                        self.gameModel.isGamePause = False
                        # 避免title cover重复显示
                        self.gameModel.selectedChart = None
                        self.gameModel.gameLoop = 'Title'
            # 滑条滑动事件
            elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.titleUIDict['DropSpeedSlider']:
                    # 更新值和UI
                    self.gameSetting.noteSpeed = event.value
                    self.titleUIDict["DropSpeedSliderValue"].set_text(str(event.value))
                elif event.ui_element == self.titleUIDict['ODSlider']:
                    # 更新值和UI
                    self.gameSetting.OD = event.value
                    self.gameSetting.cal_judgement_timing()
                    self.titleUIDict["ODSliderValue"].set_text(str(event.value))
                elif event.ui_element == self.titleUIDict['OffsetSlider']:
                    # 更新值和UI
                    self.gameSetting.offset = event.value
                    self.titleUIDict["OffsetSliderValue"].set_text(str(event.value)+'ms')
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
            _str = f"{chart.version} by {chart.creator}"
            _chartOptions.append(_str)
            self.chartDropDownMenuDict[_str] = chart

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
        pygame.time.set_timer(self.JUDGEMENT_HIDE_EVENT, 300)

    # # 更新变化信息 在这里调用
    def update_variable_text(self):
        self.variableLabelDict['Combo'].set_text(str(self.playerModel.combo))
        self.variableLabelDict['Accuracy'].set_text(str(self.playerModel.accuracy) + '%')
        self.variableLabelDict['Score'].set_text(str(self.playerModel.score))

        # 静态字 可优化
        self.variableLabelDict['SongTitleText'].set_text(str(self.levelModel.currentSong.artist + " - " + self.levelModel.currentSong.title))
        self.variableLabelDict['VersionText'].set_text(f"{self.levelModel.currentChart.version} by {self.levelModel.currentChart.creator}")

        self.variableLabelDict['PPerfectCount'].set_text(f"{'Perfect: '} {self.playerModel.pPerfectCount:>{5}}")
        self.variableLabelDict['PerfectCount'].set_text(f"{'Perfect: '} {self.playerModel.perfectCount:>{5}}")
        self.variableLabelDict['GreatCount'].set_text(f"{'Great: '} {self.playerModel.greatCount:>{5}}")
        self.variableLabelDict['CoolCount'].set_text(f"{'Cool: '} {self.playerModel.coolCount:>{5}}")
        self.variableLabelDict['BadCount'].set_text(f"{'Bad: '} {self.playerModel.badCount:>{5}}")
        self.variableLabelDict['MissCount'].set_text(f"{'Miss: '} {self.playerModel.missCount:>{5}}")
        self.variableLabelDict['FastCount'].set_text(f"{'Fast: '} {self.playerModel.fastCount:>{5}}")
        self.variableLabelDict['LateCount'].set_text(f"{'Late: '} {self.playerModel.lateCount:>{5}}")

        self.variableLabelDict['Fps'].set_text(str(round(self.pygameClock.get_fps())))

    # ------------------------------ UI 显示控制 ----------------------------------
    def kill_title_ui(self):
        for ui in self.titleUIDict.values():
            ui.kill()

    def kill_game_ui(self):
        for ui in self.judgementLabelDict.values():
            ui.kill()
        for ui in self.variableLabelDict.values():
            ui.kill()

        self.gameSpriteGroup.empty()

    def kill_score_ui(self):
        for ui in self.scoreUIDict.values():
            ui.kill()

    def show_pause_panel(self, value: bool):
        if value:
            self.variableLabelDict['PausePanel'].show()
        else:
            self.variableLabelDict['PausePanel'].hide()

    # ----------------------- draw -------------------------------
    def draw_front_ui(self, screen):
        self.uiManager.draw_ui(screen)

    def draw_background(self, screen):
        screen.blit(self.levelModel.backgroundImage, self.levelModel.backgroundImage.get_rect())

    def draw_game_sprite(self, screen):
        self.gameSpriteGroup.draw(screen)