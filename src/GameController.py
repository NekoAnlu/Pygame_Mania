import os
from math import sqrt

import pygame
import pygame_gui
from pygame_gui.elements import *

from src.Grahpic.ManiaSprite import *
from Model.GameModel import *
from Model.SettingModel import *
from Converter import *
from UIManager import *

class ManiaGame:
    def __init__(self, screen):
        # 初始化各种数据模型
        self.gameModel = GameModel()
        self.levelModel = LevelModel()
        self.uiModel = ManiaUIModel()
        self.gameSetting = GameSetting()
        self.playerModel = PlayerModel()

        # pygame相关
        self.pygameClock = pygame.time.Clock()
        pygame.mixer.init()
        self.screen = screen

        # 管理器
        self.uiManager = UIManager(self.gameModel, self.levelModel, self.playerModel, self.gameSetting, self.pygameClock)

        # 控制器
        self.gameController = GameController(self.levelModel, self.uiModel, self.gameModel, self.gameSetting, self.playerModel, self.pygameClock, self.uiManager)
        self.titlePageController = TitlePageController(self.gameModel, self.uiManager, self.pygameClock)
        self.scorePageController = ScorePageController(self.gameSetting, self.uiManager, self.playerModel, self.levelModel, self.pygameClock)

        # 值
        self.currLoop = ''  # Title Game Result
        self.gameSetting.deltaTime = self.pygameClock.tick(1000) / 1000

    def game_page_loop(self):
        # self.gameController.load_game_resource()
        self.gameController.game_start(self.screen)

    def title_page_loop(self):
        self.titlePageController.draw_title_page(self.screen)

    def score_page_loop(self):
        self.scorePageController.draw_score_page(self.screen)

    # 监控loop变化
    def on_switch_loop(self):
        if self.gameModel.gameLoop != self.currLoop:
            if self.gameModel.gameLoop == 'Game':
                # 如果是从title跳转来的
                if self.currLoop == 'Title':
                    self.reset_game_play_model()
                    self.gameController.load_game_resource(self.gameModel.selectedChart.filePath)
                    self.uiManager.kill_title_ui()
                    self.currLoop = 'Game'
                # 如果是retry
                elif self.currLoop == 'Score':
                    self.reset_game_play_model()
                    print(self.gameModel.selectedChart.filePath)
                    self.gameController.load_game_resource(self.gameModel.selectedChart.filePath)
                    self.uiManager.kill_score_ui()
                    self.currLoop = 'Game'
            elif self.gameModel.gameLoop == 'Score':
                self.uiManager.kill_game_ui()
                self.scorePageController.init_score_page()
                self.currLoop = 'Score'
            elif self.gameModel.gameLoop == 'Title':
                self.uiManager.kill_score_ui()
                self.titlePageController.init_title_page()
                self.currLoop = 'Title'
                # self.titlePageController.

    # 页面管理
    def game_loop(self):
        if self.currLoop == 'Title':
            self.title_page_loop()
        elif self.currLoop == 'Game':
            self.game_page_loop()
        elif self.currLoop == 'Score':
            self.score_page_loop()

    def reset_game_play_model(self):
        self.levelModel.__init__()
        self.playerModel.__init__()


class GameController:

    def __init__(self, level_model: LevelModel, ui_model: ManiaUIModel, game_model: GameModel
                 , game_setting: GameSetting, player_model: PlayerModel, pygame_clock: Clock, ui_manager: UIManager):

        # 初始化数据模型
        self.levelModel = level_model
        self.uiModel = ui_model
        self.gameSetting = game_setting
        self.playerModel = player_model
        self.gameModel = game_model

        # 精灵组
        self.noteSpritesGroup = pygame.sprite.Group()
        self.uiSpritesGroup = pygame.sprite.Group()

        self.pygameClock = pygame_clock

        # 初始化管理器
        self.uiManager = ui_manager

        # 音乐结束事件
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 8)

        self.isMusicPlayed = False

    def load_game_resource(self, chart_path):
        # UI重置
        self.noteSpritesGroup.empty()
        self.uiSpritesGroup.empty()

        self.isMusicPlayed = False

        # 读谱面
        self.levelModel.currentSong = MCConverter.mc_converter(chart_path)
        self.levelModel.currentChart = self.levelModel.currentSong.charts[0]
        # 读默认设置
        self.levelModel.noteSpeed = self.gameSetting.noteSpeed * 100
        # 处理按键
        self.preprocess_notes()

        # 读歌曲前清空之前的歌曲
        # pygame.mixer.music.unload()
        # pygame.mixer.pre_init(44100, 16, 2, 1024)
        pygame.mixer.music.stop()
        # pygame.mixer.music.pause()
        # pygame.mixer.music.set_pos(0)
        # pygame.mixer.music.unload()
        pygame.mixer.music.load(self.levelModel.currentChart.audioPath)
        pygame.mixer.music.play()
        pygame.mixer.music.pause()

        # 背景
        self.load_background_image()

        # 初始化UI
        self.uiManager.init_game_ui()

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
                self.levelModel.lineIndex.append(0)
            self.levelModel.noteList[_lineIndex].append(_note)
            # new 计算按键总数 LN算2note
            self.levelModel.totalNotes += 1 if _note.noteType == 0 else 2

    def play_music(self):
        if self.levelModel.leadInTime > 0:
            self.levelModel.leadInTime -= self.gameSetting.deltaTime
            if self.levelModel.leadInTime <= 0:
                pygame.mixer.music.unpause()
                self.isMusicPlayed = True
                self.levelModel.leadInTime = 0
        # if self.is_game_end():
        #     pygame.mixer.music.stop()

    def is_game_end(self) -> bool:
        for i in range(len(self.levelModel.lineIndex)):
            if self.levelModel.lineIndex[i] < len(self.levelModel.noteList[i]) or len(self.levelModel.noteQueue) != 0:
                return False
        return True
        # if self.levelModel.timer

    def spawn_notes(self):
        self.levelModel.noteSpeed = self.gameSetting.noteSpeed * 100
        _currTime = self.levelModel.timer
        _dropTime = ((self.uiModel.noteDestination - self.uiModel.noteSpawnPosition) / self.levelModel.noteSpeed) * 1000
        _lineStart = self.gameSetting.screenWidth / 2 - self.uiModel.lineWidth * len(self.levelModel.noteList) / 2.5

        for i, lineIndex in enumerate(self.levelModel.lineIndex):
            while self.levelModel.lineIndex[i] < len(self.levelModel.noteList[i]) and self.levelModel.noteList[i][self.levelModel.lineIndex[i]].startTiming <= _currTime + _dropTime:
                _x = _lineStart + self.uiModel.lineWidth * i
                # print(self.levelModel.noteList[i][self.lineIndex[i]].noteType == 0)
                if self.levelModel.noteList[i][self.levelModel.lineIndex[i]].noteType == 0:
                    _noteObj = self.levelModel.noteSpritePool.get_note((_x, self.uiModel.noteSpawnPosition),
                                                                       (_x, self.uiModel.noteDestination),
                                                                       self.levelModel.noteList[i][
                                                                           self.levelModel.lineIndex[i]].startTiming)
                    self.levelModel.noteQueue[i].append(_noteObj)
                else:
                    _noteObj = self.levelModel.lnSpritePool.get_note((_x, self.uiModel.noteSpawnPosition),
                                                                     (_x, self.uiModel.noteDestination),
                                                                     self.levelModel.noteList[i][
                                                                         self.levelModel.lineIndex[i]].startTiming,
                                                                     self.levelModel.noteList[i][
                                                                         self.levelModel.lineIndex[i]].endTiming)
                    self.levelModel.noteQueue[i].append(_noteObj)

                self.levelModel.lineIndex[i] += 1

    # 画按键的更新方法
    def draw_notes(self, screen):
        self.levelModel.noteSpritePool.add_to_group(self.noteSpritesGroup)
        self.levelModel.lnSpritePool.add_to_group(self.noteSpritesGroup)
        self.noteSpritesGroup.update(self.levelModel.noteSpeed, self.levelModel.timer, self.gameSetting)
        self.noteSpritesGroup.draw(screen)

    def draw_background_ui(self, screen):
        screen.blit(self.levelModel.backgroundImage, self.levelModel.backgroundImage.get_rect())
        self.uiSpritesGroup.draw(screen)

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
                    # LN正常按下
                    if not _note.isHolding:
                        self.timing_judgement(_offset, _note)
                        _note.isHolding = True
                    # LN尾巴判定且没有提前松手
                    elif is_key_up and _note.isHolding:
                        self.timing_judgement(_offset, _note)
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
        # self.update_judgement_text(judge_name)
        self.uiManager.update_judgement_text(judge_name)
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
            self.playerModel.maxCombo = max(self.playerModel.combo, self.playerModel.maxCombo)
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
                if len(self.levelModel.noteQueue[i]) > 0 and self.levelModel.noteQueue[i][j].noteType == 1:
                    if self.levelModel.noteQueue[i][j].isHeadMiss and not self.levelModel.noteQueue[i][j].isHeadMissCount:
                        self.levelModel.noteQueue[i][j].isHeadMissCount = True
                        self.note_judgement('Miss')
                    if self.levelModel.noteQueue[i][j].isTailMiss and not self.levelModel.noteQueue[i][
                        j].isTailMissCount:
                        self.levelModel.noteQueue[i][j].isTailMissCount = True
                        self.note_judgement('Miss')

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

    # ---------------------事件处理-----------------------------
    def on_key_press_event(self, key_event):
        # temp
        self.uiManager.gameSpriteGroup.update(key_event)
        self.hit_note_event(key_event)

    def process_user_event(self, user_event):
        if user_event.type >= pygame.USEREVENT + 32:
            self.uiManager.process_ui_event(user_event)
        # 音乐结束事件
        elif user_event.type == pygame.USEREVENT + 8:
            # 切换page
            pygame.mixer.music.stop()
            self.gameModel.gameLoop = 'Score'

    # ------------------------------ 主循环 ------------------------

    def game_start(self, screen):
        # 每帧调用设置fps
        self.gameSetting.deltaTime = self.pygameClock.tick(1000)

        # 更新Timer
        self.levelModel.timer = pygame.mixer.music.get_pos() - self.levelModel.leadInTime

        print(pygame.mixer.music.get_pos())

        # Lead In
        if not self.isMusicPlayed:
            self.play_music()

        # 清空之前的group(在修改group内变量前清空避免报错
        self.noteSpritesGroup.empty()

        # 一些数据更新
        self.uiManager.update_variable_text()
        self.uiManager.update_ui()
        self.update_note_queue()
        # self.update_variable_text()

        # 生成按键精灵
        self.spawn_notes()

        # 渲染 (注意图层)
        self.draw_background_ui(screen)
        self.uiManager.draw_back_ui(screen)
        self.draw_notes(screen)
        self.uiManager.draw_front_ui(screen)
        # self.draw_front_ui(screen)

        pygame.display.update()


class TitlePageController:
    def __init__(self, beatmaps_model: GameModel, ui_manager: UIManager, pygame_clock):
        self.beatmapsModel = beatmaps_model

        self.uiManager = ui_manager
        self.pygameClock = pygame_clock

        self.preload_beatmap()

    def init_title_page(self):
        self.uiManager.init_title_ui()
        self.uiManager.fill_title_dropdown_menu()

    def draw_title_page(self, screen: Surface):
        # 每帧调用设置fps
        self.pygameClock.tick(1000)
        screen.fill((59, 79, 110))
        self.uiManager.update_ui()
        self.uiManager.draw_front_ui(screen)
        pygame.display.update()

    def preload_beatmap(self):
        for root, dirs, files in os.walk("../beatmaps"):
            for file in files:
                if file.endswith('.mc'):
                    if root not in self.beatmapsModel.songDict:
                        self.beatmapsModel.songDict[root] = MCConverter.mc_pre_converter(root)


class ScorePageController:
    def __init__(self, game_setting: GameSetting, ui_manager: UIManager,
                 player_model: PlayerModel, level_model: LevelModel, pygame_clock):
        self.gameSetting = game_setting
        self.levelModel = level_model
        self.gameSetting = game_setting
        self.playerModel = player_model

        self.uiManager = ui_manager
        self.pygameClock = pygame_clock

    def init_score_page(self):
        self.uiManager.init_score_ui()
        self.uiManager.fill_score_page_value()


    def draw_score_page(self, screen: Surface):
        # 每帧调用设置fps
        self.pygameClock.tick(1000)
        screen.fill((59, 79, 110))
        self.uiManager.update_ui()
        self.uiManager.draw_front_ui(screen)
        pygame.display.update()
