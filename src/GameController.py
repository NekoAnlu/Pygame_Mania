import pygame
from pygame import *
from pygame.locals import *

from Model.BeatmapModel import *
from Model.GameModel import *
from Converter import *
from src.Grahpic.ManiaSprite import *


class ManiaGame:

    lineIndex: List[int] = []
    leadInTime: int = 2000

    def __init__(self):

        # 初始化数据模型
        self.levelModel = LevelModel()
        self.uiModel = ManiaUIModel()
        self.gameModel = GameModel()

        # pygame相关
        pygame.mixer.init()
        self.noteSpritesGroup = pygame.sprite.Group()
        self.uiSpritesGroup = pygame.sprite.Group()
        self.pygameClock = pygame.time.Clock()

        self.gameModel.deltaTime = self.pygameClock.tick(120)

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

        _image = pygame.transform.smoothscale(_image, (_image.get_height()*_scaleFactor, _image.get_width()*_scaleFactor))

        # 居中
        _image.get_rect(center=(1920/2, 1080/2))

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
            # 动态判断谱面key数并生成对应数量的队列
            while len(self.levelModel.noteQueue) <= _lineIndex:
                self.levelModel.noteQueue.append([])
                self.lineIndex.append(0)
            self.levelModel.noteQueue[_lineIndex].append(_note)

    def init_ui(self):
        # ManiaPanel
        _maniaPanel = ManiaPanelSprite((self.uiModel.lineStart + (self.uiModel.lineWidth * (len(self.levelModel.noteQueue)/2-0.5)), 0), self.uiModel.lineWidth * len(self.levelModel.noteQueue) * 1.1)
        self.uiSpritesGroup.add(_maniaPanel)

        # HitPosition
        for i in range(len(self.levelModel.noteQueue)):
            _lineSprite = HitPositionSprite((self.uiModel.lineStart + self.uiModel.lineWidth * i, self.uiModel.noteDestination),i)
            self.uiSpritesGroup.add(_lineSprite)

    def play_music(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

    def spawn_notes(self):
        _currTime = self.levelModel.timer
        _dropTime = ((self.uiModel.noteDestination - self.uiModel.noteSpawnPosition) / self.levelModel.noteSpeed) * 1000

        for i, lineIndex in enumerate(self.lineIndex):
            while self.lineIndex[i] < len(self.levelModel.noteQueue[i]) and self.levelModel.noteQueue[i][self.lineIndex[i]].startTiming <= _currTime + _dropTime:
                _x = self.uiModel.lineStart + self.uiModel.lineWidth * i
                _noteObj = self.levelModel.noteSpritePool.get_note((_x, self.uiModel.noteSpawnPosition), (_x, self.uiModel.noteDestination), self.levelModel.noteQueue[i][self.lineIndex[i]].startTiming)
                self.lineIndex[i] += 1

    # 画按键的更新方法
    def draw_notes(self, screen):
        self.levelModel.noteSpritePool.add_to_group(self.noteSpritesGroup)

        self.noteSpritesGroup.update(self.levelModel.noteSpeed, self.levelModel.timer)
        self.noteSpritesGroup.draw(screen)

    def draw_ui(self, screen):
        screen.blit(self.levelModel.backgroundImage, self.levelModel.backgroundImage.get_rect())
        self.uiSpritesGroup.draw(screen)

    def game_start(self, screen):
        # 更新Timer
        self.levelModel.timer = pygame.mixer.music.get_pos() - self.leadInTime

        # 清空之前的group(在修改group内变量前清空避免报错
        self.noteSpritesGroup.empty()

        # 生成按键精灵
        self.spawn_notes()

        # 渲染 (注意图层)
        self.draw_ui(screen)
        self.draw_notes(screen)

        # Lead In
        self.leadInTime -= self.gameModel.deltaTime
        if self.leadInTime <= 0:
            self.play_music()
            self.leadInTime = 0

    # 以下为事件处理
    def on_key_press(self, keyevent):
        self.uiSpritesGroup.update(keyevent)
        #if key == pygame.K_d:
            # self.uiSpritesGroup.



# game = ManiaGame()
# game.test()