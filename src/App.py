import pygame
import cProfile
from pygame.locals import *
from GameController import ManiaGame
from Grahpic import ManiaSprite
from src.Model.SettingModel import GameSetting


class ManiaPygame:
    gameController: ManiaGame

    def __init__(self):
        self.running = True
        self.screen = None
        # self.clock = pygame.time.Clock()
        self.size = self.weight, self.height = GameSetting.screenWidth, GameSetting.screenHeight
        self.gameController = ManiaGame()

        # note = NoteSprite((200, 200))
        # hitPosition = HitPositionSprite((500, 500))
        # self.spritesGroup = pygame.sprite.Group()d
        # self.spritesGroup.add(note)
        # self.spritesGroup.add(hitPosition)

    def on_init(self):
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        # temp
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF, 16)
        self.gameController.load_resource()
        # self.screen.blit(self.gameController.levelModel.backgroundImage, self.gameController.levelModel.backgroundImage.get_rect())

        self.running = True

    def on_event(self):
        # 坑1：检测键盘字母区按下事件只能在获取event循环里接收 不能传 会被TextInput事件覆盖
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.gameController.on_key_press_event(event)


    def on_loop(self):
        pass
        # dt = self.clock.tick(1000) / 1000
        # self.gameController.levelModel.timer += dt

        # pygame.surface.Surface.blit(self.screen,)

    def on_render(self):
        self.gameController.game_start(self.screen)

        pygame.display.flip()

    # on_cleanup call pygame.quit() that quits all PyGame modules. Anything else will be cleaned up by Python.
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        # if not self.on_init():
        #     self._running = False

        while self.running:
            # event()
            # for event in pygame.event.get():
            self.on_event()
            # loop()
            self.on_loop()
            # render()
            self.on_render()

        self.on_cleanup()


profiler = cProfile.Profile()
profiler.enable()

theApp = ManiaPygame()
theApp.on_init()
theApp.on_execute()

profiler.disable()


profiler.print_stats(sort='time')
