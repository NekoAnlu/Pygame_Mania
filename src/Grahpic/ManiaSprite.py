import pygame


class NoteSprite(pygame.sprite.Sprite):

    drawSize = (20, 20)
    realSize = (100, 100)

    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface(self.drawSize)
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))  # 设置黑色为透明色

        self.color = (0, 0, 255)
        pygame.draw.circle(self.image, self.color, (10, 10), 10)

        # 小图放大做出像素效果
        self.image = pygame.transform.scale(self.image, self.realSize)

        # 控制sprite位置
        self.rect = self.image.get_rect(center=position)


class HitPositionSprite(pygame.sprite.Sprite):
    drawSize = (20, 20)
    realSize = (100, 100)

    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface(self.drawSize)

        # 透明背景
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        self.color = (0, 0, 255)
        pygame.draw.circle(self.image, self.color, (10, 10), 10, 1)

        # 小图放大做出像素效果
        self.image = pygame.transform.scale(self.image, self.realSize)

        # 控制sprite位置
        self.rect = self.image.get_rect(center=position)
