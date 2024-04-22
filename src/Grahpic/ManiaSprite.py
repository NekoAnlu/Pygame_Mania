from typing import List

import pygame
from pygame.locals import *

class NoteSprite(pygame.sprite.Sprite):

    drawSize = (20, 20)
    realSize = (100, 100)

    def __init__(self, spawn_position, target_position, timing):
        super().__init__()
        self.image = pygame.Surface(self.drawSize)
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))  # 设置黑色为透明色
        self.color = (0, 0, 255)
        pygame.draw.circle(self.image, self.color, (10, 10), 10)
        # 小图放大做出像素效果
        self.image = pygame.transform.scale(self.image, self.realSize)
        # 控制sprite位置
        self.rect = self.image.get_rect(center=spawn_position)
        # 移动用变量
        self.spawnPosition = spawn_position
        self.targetPosition = target_position
        # 按键的时值
        self.timing = timing
        # 案件池用变量
        self.active = True

    def update(self, speed, timer):
        if self.active:
            # 每毫秒移动的距离 in px
            _speedInUnit = 1000 / speed
            # 当前时间
            _currTime = timer
            # 移动距离
            _moveY = (_currTime - self.timing) / _speedInUnit
            self.rect.centery = self.targetPosition[1] + _moveY

        # 检查是否被击打或者移出屏幕外（miss）
        self.check_inactive()


    def check_inactive(self):
        if self.rect.centery > 1080:
            self.active = False


# 按键对象池
class NoteSpritePool:
    def __init__(self):
        self.notePool: List[NoteSprite] = []

    def get_note(self, spawn_position, target_position, timing):
        for note in self.notePool:
            if not note.active:
                note.__init__(spawn_position, target_position, timing)
                return note

        # 如果无则扩展池
        new_note = NoteSprite(spawn_position, target_position, timing)
        self.notePool.append(new_note)
        return new_note

    # 每一帧把对象池里的sprite加入spritegroup中以便绘图
    def add_to_group(self, group):
        for note in self.notePool:
            if note.active:
                group.add(note)


class HitPositionSprite(pygame.sprite.Sprite):
    drawSize = (20, 20)
    realSize = (100, 100)

    def __init__(self, position, index):
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

        # 对象变量
        self.index = index

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and self.index == 0:
                self.fill()
            elif event.key == pygame.K_f and self.index == 1:
                self.fill()
            elif event.key == pygame.K_j and self.index == 2:
                self.fill()
            elif event.key == pygame.K_k and self.index == 3:
                self.fill()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN and self.index == 0:
                self.un_fill()
                print(2)
            elif event.key == pygame.K_f and self.index == 1:
                self.un_fill()
            elif event.key == pygame.K_j and self.index == 2:
                self.un_fill()
            elif event.key == pygame.K_k and self.index == 3:
                self.un_fill()

    def fill(self):
        pygame.draw.circle(self.image, self.color, (10, 10), 10)
        self.image = pygame.transform.scale(self.image, self.realSize)

    def un_fill(self):
        pygame.draw.circle(self.image, self.color, (10, 10), 10, 1)
        self.image = pygame.transform.scale(self.image, self.realSize)

class ManiaPanelSprite(pygame.sprite.Sprite):
    def __init__(self, position, size_x):
        super().__init__()
        self.drawSize = (size_x, 1080)
        self.image = pygame.Surface(self.drawSize)

        # 更黑的叠层
        self.image.fill((0, 0, 0))
        self.image.set_alpha(250)

        self.rect = self.image.get_rect(midtop=position)
