import pygame
from pygame.locals import *


class ManiaPygame:
    def __init__(self):
        self._running = True
        self._screen = None
        self._clock = pygame.time.Clock()
        self.size = self.weight, self.height = 1920, 1080

    # on_init calls pygame.init() that initialize all PyGame modules. Then it create main display - 640x400 window and try to use hardware acceleration. At the end this routine sets _running to True.
    def on_init(self):
        pygame.init()
        self._screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    # on_event check if Quit event happened if so sets _running to False wich will break game loop.
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        dt = self._clock.tick(60) / 1000

    def on_render(self):
        self._screen.fill("purple")
        pygame.draw.circle(self._screen, "red", (0,0), 40)
        pygame.display.flip()

    # on_cleanup call pygame.quit() that quits all PyGame modules. Anything else will be cleaned up by Python.
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        # if not self.on_init():
        #     self._running = False

        while self._running:
            # event()
            for event in pygame.event.get():
                self.on_event(event)
            # loop()
            self.on_loop()
            # render()
            self.on_render()

        self.on_cleanup()


# theApp = App()
# theApp.on_init()
# theApp.on_execute()
