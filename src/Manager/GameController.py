import os
from math import sqrt

from src.Utils.ConfigParser import ConfigParser
from src.Model.GameModel import *
from src.Model.SettingModel import *
from src.Utils.Converter import *
from src.Manager.UIManager import *


class ManiaGame:
    def __init__(self, screen):
        # 初始化各种数据模型
        self.gameModel = GameModel()
        self.levelModel = LevelModel()
        self.maniaSetting = ManiaSetting()
        self.gameSetting = GameSetting()
        self.playerModel = PlayerModel()

        # pygame相关
        self.pygameClock = pygame.time.Clock()
        pygame.mixer.init()
        self.screen = screen

        # config设置
        self.config = ConfigParser()
        self.config.init_mania_setting(self.maniaSetting)

        # ui管理器
        self.uiManager = UIManager(self.gameModel, self.levelModel, self.playerModel, self.gameSetting, self.maniaSetting, self.pygameClock)

        # 控制器
        self.gameController = GameController(self.levelModel, self.maniaSetting, self.gameModel, self.gameSetting, self.playerModel, self.pygameClock, self.uiManager)
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
            # 偷懒用重开方法
            if self.gameModel.gameLoop == 'Game' or self.gameModel.gameLoop == 'GameRetry':
                self.uiManager.kill_game_ui()
                self.uiManager.kill_title_ui()
                self.uiManager.kill_score_ui()
                self.reset_game_play_model()
                self.gameController.load_game_resource(self.gameModel.selectedChart.filePath)
                self.gameModel.gameLoop = 'Game'
                self.currLoop = 'Game'
            elif self.gameModel.gameLoop == 'Score':
                self.uiManager.kill_game_ui()
                self.scorePageController.init_score_page()
                self.currLoop = 'Score'
            elif self.gameModel.gameLoop == 'Title':
                self.uiManager.kill_game_ui()
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
    def __init__(self, level_model: LevelModel, mania_setting: ManiaSetting, game_model: GameModel
                 , game_setting: GameSetting, player_model: PlayerModel, pygame_clock: Clock, ui_manager: UIManager):

        # 初始化数据模型
        self.levelModel = level_model
        self.maniaSetting = mania_setting
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
        # pygame.mixer.music.set_endevent(pygame.USEREVENT + 8)

        # 一些flag
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
        # pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(80)
        pygame.mixer.music.load(self.levelModel.currentChart.audioPath)
        pygame.mixer.music.play()
        # 如果第一个按键离音乐开头太远就直接播
        if self.levelModel.firstNoteTiming > 5000:
            pygame.mixer.music.set_pos((self.levelModel.firstNoteTiming - 3000)/1000.0)
            self.levelModel.leadInTime = 1
            self.levelModel.skipTime = self.levelModel.firstNoteTiming - 3000
        pygame.mixer.music.pause()

        # 背景
        # self.load_background_image()

        # 初始化UI
        self.uiManager.init_game_ui()

    # 把note按轨道位置分为4个队列
    def preprocess_notes(self):
        for _note in self.levelModel.currentChart.noteList:
            _lineIndex = _note.line
            # 计算按键总数
            self.levelModel.totalNotes += 1
            # new offset
            _note.startTiming += self.gameSetting.offset
            if _note.noteType == 1:
                _note.endTiming += self.gameSetting.offset
            # 记录第一个按键
            self.levelModel.firstNoteTiming = min(self.levelModel.firstNoteTiming, _note.startTiming)
            # 动态判断谱面key数初始化对应数量的队列和列表
            while len(self.levelModel.noteList) <= _lineIndex:
                self.levelModel.noteList.append([])
                self.levelModel.noteQueue.append([])
                self.levelModel.lineIndex.append(0)
            self.levelModel.noteList[_lineIndex].append(_note)

    def spawn_notes(self):
        self.levelModel.noteSpeed = self.gameSetting.noteSpeed * 100
        _currTime = self.levelModel.timer
        _dropTime = ((self.maniaSetting.hitPosition - self.maniaSetting.noteSpawnPosition) / self.levelModel.noteSpeed) * 1000
        _lineStart = self.gameSetting.screenWidth / 2 - self.maniaSetting.lineWidth * (self.levelModel.currentChart.columnNum / 2.0 - 0.5)
        for i, lineIndex in enumerate(self.levelModel.lineIndex):
            while self.levelModel.lineIndex[i] < len(self.levelModel.noteList[i]) and self.levelModel.noteList[i][self.levelModel.lineIndex[i]].startTiming <= _currTime + _dropTime:
                _x = _lineStart + self.maniaSetting.lineWidth * i
                # print(self.levelModel.noteList[i][self.lineIndex[i]].noteType == 0)
                if self.levelModel.noteList[i][self.levelModel.lineIndex[i]].noteType == 0:
                    _noteObj = self.levelModel.noteSpritePool.get_note(self.maniaSetting.noteSize, self.maniaSetting.noteColor,
                                                                       (_x, self.maniaSetting.noteSpawnPosition),
                                                                       (_x, self.maniaSetting.hitPosition),
                                                                       self.levelModel.noteList[i][
                                                                           self.levelModel.lineIndex[i]].startTiming)
                    self.levelModel.noteQueue[i].append(_noteObj)
                else:
                    _noteObj = self.levelModel.lnSpritePool.get_note(self.maniaSetting.noteSize, self.maniaSetting.noteColor,
                                                                     self.maniaSetting.lnBodyColor,
                                                                     (_x, self.maniaSetting.noteSpawnPosition),
                                                                     (_x, self.maniaSetting.hitPosition),
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

    # -------------------- 游戏流程控制相关 ---------------------
    def play_music(self):
        if self.levelModel.leadInTime > 0:
            self.levelModel.leadInTime -= self.gameSetting.deltaTime
            if self.levelModel.leadInTime <= 0:
                pygame.mixer.music.unpause()
                self.isMusicPlayed = True
                self.levelModel.leadInTime = 0
        # if self.is_game_end():
        #     pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        # 防止leadin的时候出问题
        if self.isMusicPlayed:
            pygame.mixer.music.unpause()

    def is_game_end(self) -> bool:
        for i in range(len(self.levelModel.lineIndex)):
            if self.levelModel.lineIndex[i] < len(self.levelModel.noteList[i]) or len(self.levelModel.noteQueue[i]) != 0:
                return False
        return True
        # if self.levelModel.timer

    # 检测游戏结束 并跳转
    def check_game_end(self):
        if self.is_game_end():
            self.levelModel.leadOutTime -= self.gameSetting.deltaTime
            if self.levelModel.leadOutTime <= 0:
                pygame.mixer.music.fadeout(500)
                self.levelModel.leadOutTime = 0
                pygame.mixer.music.stop()
                self.gameModel.gameLoop = 'Score'

    # --------------------判定相关 UI 逻辑-------------------------
    def hit_note_event(self, key_event):
        _columnNum = self.levelModel.currentChart.columnNum
        if key_event.type == pygame.KEYDOWN:
            for i in range(0, _columnNum):
                if key_event.key == self.maniaSetting.keyBindDict[_columnNum][i]:
                    self.on_hit_note(i, self.levelModel.timer, False)
        if key_event.type == pygame.KEYUP:
            for i in range(0, _columnNum):
                if key_event.key == self.maniaSetting.keyBindDict[_columnNum][i]:
                    self.on_hit_note(i, self.levelModel.timer, True)

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
                    _offset = _note.timing - timing
                else:
                    _offset = _note.endTiming - timing
            else:
                _offset = _note.timing - timing

            # LN
            if _note.noteType == 1:
                # 如果头miss了但中途按下
                if not is_key_up and _note.isHeadMiss and not _note.isHolding:
                    _note.isHeld = True
                    _note.isHolding = True

                # LN头判定
                if not is_key_up:
                    if abs(_offset) <= self.gameSetting.timing_Cool:
                        # LN正常按下
                        if not _note.isHeld and not _note.isHolding:
                            # self.timing_judgement(_offset, _note, 'Head')
                            _note.isHolding = True
                            _note.isHeld = True
                            _note.headOffset = _offset
                    elif abs(_offset) <= self.gameSetting.timing_Miss:
                        if not _note.isHeld and not _note.isHolding:
                            _note.isHeadMiss = True
                            _note.isHeld = True
                            _note.isHolding = True
                            _note.isBad = True
                            _note.headOffset = 99999
                # LN尾巴判定
                else:
                    if abs(_offset) <= self.gameSetting.timing_Miss:
                        if _note.isHolding and not _note.isHeadMiss:
                            self.timing_judgement(_offset, _note)
                            _note.isHolding = False
                            _note.active = False
                            self.levelModel.noteQueue[line_index].pop(0)
                        # 如果头miss了 继续按下无论什么时候松都是bad
                        elif _note.isHolding and _note.isHeadMiss:
                            _note.isHolding = False
                            _note.isBad = True
                    # 长条尾提前松手判定bad
                    else:
                        if _note.isHolding:
                            _note.isBad = True
                            _note.isHolding = False
                            _note.isHeadMiss = True

            # 普通按键是否在可判定区间内
            elif _note.noteType == 0 and abs(_offset) <= self.gameSetting.timing_Miss:
                # 基础判定
                self.timing_judgement(_offset, _note)
                # 如果是普通按键直接回收并隐藏
                _note.active = False
                self.levelModel.noteQueue[line_index].pop(0)

    # 判定信息显示 + 数据更新
    # 判定时值为OM Score V1
    # https://osu.ppy.sh/wiki/en/Gameplay/Judgement/osu%21mania
    def timing_judgement(self, _offset, _note):
        # RC
        if _note.noteType == 0:
            # 判定fast和late
            _isFast = _offset > 0
            _offset = abs(_offset)
            if _offset <= self.gameSetting.timing_Bad:
                if _offset <= self.gameSetting.timing_PPerfect:
                    self.note_judgement('PPerfect', _isFast)
                elif _offset <= self.gameSetting.timing_Perfect:
                    self.note_judgement('Perfect', _isFast)
                elif _offset <= self.gameSetting.timing_Great:
                    self.note_judgement('Great', _isFast)
                elif _offset <= self.gameSetting.timing_Cool:
                    self.note_judgement('Cool', _isFast)
                else:
                    self.note_judgement('Bad', _isFast)
            else:
                self.note_judgement('Miss', _isFast)
        # 正常判定下的LN
        else:
            # print(f'{_offset} {_note.headOffset}')
            # 判定fast和late
            _isFast = (_offset + _note.headOffset) > 0
            _offset = abs(_offset) + abs(_note.headOffset)
            if _note.headOffset <= self.gameSetting.timing_PPerfect * 1.2 and _offset <= self.gameSetting.timing_PPerfect * 2.4:
                self.note_judgement('PPerfect', _isFast)
            elif _note.headOffset <= self.gameSetting.timing_Perfect * 1.1 and _offset <= self.gameSetting.timing_Perfect * 2.2:
                self.note_judgement('Perfect', _isFast)
            elif _note.headOffset <= self.gameSetting.timing_Great and _offset <= self.gameSetting.timing_Great * 2:
                self.note_judgement('Great', _isFast)
            elif _note.headOffset <= self.gameSetting.timing_Cool and _offset <= self.gameSetting.timing_Cool * 2:
                self.note_judgement('Cool', _isFast)
            else:
                self.note_judgement('Bad', _isFast)

    # 具体判定对view和model的更新
    def note_judgement(self, judge_name, is_fast=False):
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
            self.playerModel.maxCombo = max(self.playerModel.combo, self.playerModel.maxCombo)
            self.playerModel.combo = 0
        elif judge_name == 'Miss':
            self.playerModel.missCount += 1
            self.playerModel.maxCombo = max(self.playerModel.combo, self.playerModel.maxCombo)
            self.playerModel.combo = 0

        # fast late 在不是大P和miss的时候记录
        if judge_name != 'PPerfect' and judge_name != 'Miss':
            if is_fast:
                self.playerModel.fastCount += 1
            else:
                self.playerModel.lateCount += 1

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
            while len(self.levelModel.noteQueue[i]) > 0 and self.levelModel.noteQueue[i][0].noteType == 1 and (self.levelModel.noteQueue[i][0].isMiss or self.levelModel.noteQueue[i][0].isBad):
                if self.levelModel.noteQueue[i][0].isMiss:
                    self.note_judgement('Miss')
                    self.levelModel.noteQueue[i].pop(0)
                elif self.levelModel.noteQueue[i][0].isBad:
                    self.note_judgement('Bad')
                    self.levelModel.noteQueue[i].pop(0)

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
        if self.gameModel.gameLoop == 'Game':
            if key_event.type == pygame.KEYDOWN:
                if key_event.key == pygame.K_ESCAPE:
                    if not self.gameModel.isGamePause:
                        self.gameModel.isGamePause = True
                        self.uiManager.show_pause_panel(True)
                        self.pause_music()
                    else:
                        self.gameModel.isGamePause = False
                        self.uiManager.show_pause_panel(False)
                        self.resume_music()
            # 按键提示
            self.uiManager.gameSpriteGroup.update(key_event, len(self.levelModel.noteQueue))
            self.hit_note_event(key_event)

    def process_user_event(self, user_event):
        if user_event.type >= pygame.USEREVENT + 32:
            self.uiManager.process_ui_event(user_event)
        # # 音乐结束事件
        # elif user_event.type == pygame.USEREVENT + 8:
        #     # 切换page
        #     pygame.mixer.music.stop()
        #     self.gameModel.gameLoop = 'Score'

    # ------------------------------ 主循环 ------------------------

    def game_start(self, screen):
        # 每帧调用设置fps
        self.gameSetting.deltaTime = self.pygameClock.tick(1000)

        # Pause的时候UI照常更新
        self.uiManager.update_ui()

        if not self.gameModel.isGamePause:
            # 更新Timer
            self.levelModel.timer = pygame.mixer.music.get_pos() - self.levelModel.leadInTime + self.levelModel.skipTime

            # Lead In
            if not self.isMusicPlayed:
                self.play_music()

            # 结束
            self.check_game_end()

            # 清空之前的group(在修改group内变量前清空避免报错
            self.noteSpritesGroup.empty()

            # 一些数据更新
            self.uiManager.update_variable_text()
            # self.uiManager.update_ui()
            self.update_note_queue()

            # 生成按键精灵
            self.spawn_notes()

            # 渲染 (注意图层)
            self.uiManager.draw_background(screen)
            self.uiManager.draw_game_sprite(screen)
            self.draw_notes(screen)

        # 图层
        self.uiManager.draw_front_ui(screen)

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
        for root, dirs, files in os.walk("./beatmaps"):
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
