import pygame
from pygame.locals import *
from GameController import ManiaGame
from Grahpic import ManiaSprite
from src.Grahpic.ManiaSprite import *


class ManiaPygame:
    gameController: ManiaGame

    def __init__(self):
        self.running = True
        self.screen = None
        self.clock = pygame.time.Clock()
        self.size = self.weight, self.height = 1920, 1080
        self.gameController = ManiaGame()

        # note = NoteSprite((200, 200))
        # hitPosition = HitPositionSprite((500, 500))
        # self.spritesGroup = pygame.sprite.Group()
        # self.spritesGroup.add(note)
        # self.spritesGroup.add(hitPosition)

    def on_init(self):
        pygame.init()
        # temp
        self.gameController.load_resource()
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        # self.screen.blit(self.gameController.levelModel.backgroundImage, self.gameController.levelModel.backgroundImage.get_rect())

        self.running = True

    # on_event check if Quit event happened if so sets _running to False wich will break game loop.
    def on_event(self, event):
        self.gameController.on_key_press(event)
        if event.type == pygame.QUIT:
            self.running = False


    def on_loop(self):

        dt = self.clock.tick(120) / 1000
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
            for event in pygame.event.get():
                self.on_event(event)
            # loop()
            self.on_loop()
            # render()
            self.on_render()

        self.on_cleanup()


theApp = ManiaPygame()
theApp.on_init()
theApp.on_execute()
