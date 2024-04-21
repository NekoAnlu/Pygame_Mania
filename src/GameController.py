import pygame
from pygame import *

from Model.BeatmapModel import *
from Converter import *


class ManiaGame:

    # 界面设置
    lineWidth: int
    lineStart: int

    # 游戏相关
    currentSong: Song
    currentChart: Chart

    # 谱面数据
    noteQueue: List[List[Note]]

    # Pygame组件
    backgroundImage: Surface

    def __init__(self):
        pygame.mixer.init()
        self.lineWidth = 40

    def load_resource(self):
        # 读谱面
        converter = MCConverter()
        self.currentSong = converter.mc_converter('1')
        self.currentChart = self.currentSong.charts[0]

        # 读和处理各种资源
        self.preprocess_notes()

        pygame.mixer.music.load(self.currentChart.audioPath)
        self.load_background_image()




    def load_background_image(self):
        _image = pygame.image.load(self.currentChart.backgroundPath)

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

        self.backgroundImage = _image

    # 把note按轨道位置分为4个队列
    def preprocess_notes(self):
        for _note in self.currentChart.noteList:
            _lineIndex = _note.line
            # 动态判断谱面key数并生成对应数量的队列
            while len(self.noteQueue) <= _lineIndex:
                self.noteQueue.append([])
            self.noteQueue[_lineIndex].append(_note)

    def play_music(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

# game = ManiaGame()
# game.test()