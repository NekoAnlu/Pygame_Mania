from typing import List

import pygame
from pygame.locals import *

from src.Model.SettingModel import *
from src.Model.BeatmapModel import *


class NoteSprite(pygame.sprite.Sprite):
    drawSize = (20, 20)
    realSize = (100, 100)

    def __init__(self, spawn_position, target_position, timing):
        super().__init__()
        self.noteType = 0
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
            _speedInUnit = 1000.0 / speed
            # 当前时间
            _currTime = timer
            # 移动距离
            _moveY = (_currTime - self.timing) / _speedInUnit
            self.rect.centery = self.targetPosition[1] + _moveY

        # 检查是否被击打或者移出屏幕外（miss）
        self.check_miss(timer)

    def check_miss(self, timer):
        if timer - self.timing > GameSetting.timing_Miss:
            self.active = False


# 按键对象池
class NoteSpritePool:
    def __init__(self):
        self.notePool: List[NoteSprite] = []

    def get_note(self, spawn_position, target_position, timing) -> NoteSprite:
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


class LNSprite(pygame.sprite.Sprite):
    drawSize = (20, 20)
    realSize = (100, 100)

    def __init__(self, spawn_position, target_position, timing, end_timing):
        super().__init__()

        self.noteType = 1
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
        self.endTiming = end_timing
        self.timer = 0
        # 按键池用变量
        self.active = True
        # sp判定用
        self.isHeadMiss = False
        self.isHolding = False
        # self.lnBodyRect = Rect()

    def update(self, speed, timer):
        self.check_miss(timer)

        if self.active:
            # sp 可优化？
            _dropTime = ((self.targetPosition[1] - self.spawnPosition[1]) / float(speed)) * 1000.0
            # 每毫秒移动的距离 in px
            _speedInUnit = 1000.0 / speed
            # 当前时间
            _currTime = timer
            # 移动距离
            _moveY = (_currTime - self.timing) / _speedInUnit
            # LN拉长 需要减去droptime！
            if _currTime <= self.endTiming - _dropTime:
                _newSize = (self.drawSize[0], self.drawSize[1] + abs(self.rect.bottom)/5.0)
                self.image = pygame.Surface(_newSize)
                self.image.fill((0, 0, 0))
                self.image.set_colorkey((0, 0, 0))  # 设置黑色为透明色
                pygame.draw.circle(self.image, self.color, (10, 10), 10)
                self.lnBodyRect = pygame.draw.rect(self.image, self.color, (0, 10, 20, _newSize[1] - 20))
                pygame.draw.circle(self.image, self.color, (10, _newSize[1] - 10), 10)
                # print(self.timing)
                self.image = pygame.transform.scale(self.image, (100, _newSize[1]*5))
                self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

            if self.isHolding:
                _newHeight = max(self.rect.height - (self.targetPosition[1] + _moveY + 100) + self.rect.bottom, 0)
                print(self.rect.height - (self.targetPosition[1] + _moveY + 100) + self.rect.bottom)
                #_newHeight = self.rect.height - (self.targetPosition[1] + _moveY + 100) - self.rect.bottom
                self.image = self.image.subsurface((0, 0, self.rect.width, _newHeight))
                self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            else:
                # 移动
                self.rect.bottom = self.targetPosition[1] + _moveY + 100


    def check_miss(self, timer):
        if not self.isHolding and timer - self.timing > GameSetting.timing_Miss:
            self.isHeadMiss = True
        if timer - self.endTiming > GameSetting.timing_Miss and not self.isHolding:
            self.active = False


# 同上notepool
class LNSpritePool:
    def __init__(self):
        self.notePool: List[LNSprite] = []

    def get_note(self, spawn_position, target_position, timing, end_timing) -> LNSprite:
        for note in self.notePool:
            if not note.active:
                note.__init__(spawn_position, target_position, timing, end_timing)
                return note

        # 如果无则扩展池
        new_note = LNSprite(spawn_position, target_position, timing, end_timing)
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

        self.color = (0, 0, 255)
        self.position = position
        self.draw_unfill()

        # 对象变量
        self.index = index

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d and self.index == 0:
                self.draw_fill()
            elif event.key == pygame.K_f and self.index == 1:
                self.draw_fill()
            elif event.key == pygame.K_j and self.index == 2:
                self.draw_fill()
            elif event.key == pygame.K_k and self.index == 3:
                self.draw_fill()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d and self.index == 0:
                self.draw_unfill()
            elif event.key == pygame.K_f and self.index == 1:
                self.draw_unfill()
            elif event.key == pygame.K_j and self.index == 2:
                self.draw_unfill()
            elif event.key == pygame.K_k and self.index == 3:
                self.draw_unfill()

    def draw_fill(self):
        self.image = pygame.Surface(self.drawSize)
        pygame.draw.circle(self.image, self.color, (10, 10), 10)
        self.image = pygame.transform.scale(self.image, self.realSize)
        self.rect = self.image.get_rect(center=self.position)

    def draw_unfill(self):
        self.image = pygame.Surface(self.drawSize)
        pygame.draw.circle(self.image, self.color, (10, 10), 10, 1)
        self.image = pygame.transform.scale(self.image, self.realSize)
        self.rect = self.image.get_rect(center=self.position)


class ManiaPanelSprite(pygame.sprite.Sprite):
    def __init__(self, position, size_x):
        super().__init__()
        self.drawSize = (size_x, 1080)
        self.image = pygame.Surface(self.drawSize)

        # 更黑的叠层
        self.image.fill((0, 0, 0))
        self.image.set_alpha(250)

        self.rect = self.image.get_rect(midtop=position)


class JudgementTextSprite(pygame.sprite.Sprite):
    def __init__(self, text, text_size, color, position):
        super().__init__()
        self.font = pygame.font.Font('../font/Silver.ttf', text_size)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect(center=position)
        self.timer = 0
        self.active = False
        self.activeTime = 500  # 预设定1s自动隐藏

    # 被active了以后自动kill
    def update(self):
        if self.active:
            self.timer += pygame.time.Clock().tick(120)
            if self.timer >= self.activeTime:
                self.timer = 0
                self.active = False
        else:
            self.timer = 0
            self.kill()


class VariableTextSprite(pygame.sprite.Sprite):
    def __init__(self, text, text_size, color, position):
        super().__init__()
        self.font = pygame.font.Font('../font/Silver.ttf', text_size)
        self.color = color
        self.position = position
        self.draw_text(text)
        self.active = False
    
    def update(self, new_text):
        self.draw_text(new_text)

    def draw_text(self, text):
        if text is not str:
            text = str(text)

        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect(center=self.position)
