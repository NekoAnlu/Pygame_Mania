import pygame
import pygame_gui

from GameController import ManiaGame
from src.Model.SettingModel import GameSetting


class ManiaPygame:
    maniaGame: ManiaGame

    def __init__(self):
        self.running = True
        self.screen = None
        # self.clock = pygame.time.Clock()
        self.size = self.weight, self.height = GameSetting.screenWidth, GameSetting.screenHeight
        self.maniaGame: ManiaGame

    def on_init(self):
        pygame.mixer.pre_init(44100, 16, 2, 1024)
        pygame.init()
        # temp
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.HWSURFACE)
        # 要在pygame初始化后初始化
        self.maniaGame = ManiaGame(self.screen)

        self.running = True

    def on_event(self):
        # 坑1：检测键盘字母区按下事件只能在获取event循环里接收 不能传 会被TextInput事件覆盖
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.maniaGame.gameController.on_key_press_event(event)
            self.maniaGame.uiManager.process_ui_event(event)
            #     if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            #
            # self.maniaGame.uiManager.process_ui_event(event)
            # elif event.type >= pygame.USEREVENT:
            #     self.maniaGame.gameController.process_user_event(event)


    # on_cleanup call pygame.quit() that quits all PyGame modules. Anything else will be cleaned up by Python.
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        # if not self.on_init():
        #     self._running = False

        while self.running:
            # event()
            self.on_event()

            self.maniaGame.on_switch_loop()
            self.maniaGame.game_loop()


        self.on_cleanup()


theApp = ManiaPygame()
theApp.on_init()
theApp.on_execute()


