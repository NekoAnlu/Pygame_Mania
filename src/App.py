import pygame

from src.Manager.GameController import ManiaGame
from src.Model.SettingModel import GameSetting


class App:
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
        pygame.display.set_caption('PyMania')
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.HWSURFACE)
        # 要在pygame初始化后初始化
        self.maniaGame = ManiaGame(self.screen)

        self.running = True

    def on_event(self):
        # 坑1：检测键盘字母区按下事件只能在获取event循环里接收 不能传 会被TextInput事件覆盖
        for event in pygame.event.get():
            self.maniaGame.uiManager.process_ui_event(event)
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.maniaGame.gameController.on_key_press_event(event)
            elif event.type >= pygame.USEREVENT:
                self.maniaGame.gameController.process_user_event(event)

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        while self.running:
            self.on_event()
            self.maniaGame.on_switch_loop()
            self.maniaGame.game_loop()

        self.on_cleanup()



