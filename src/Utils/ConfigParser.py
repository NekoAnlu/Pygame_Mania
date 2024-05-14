import configparser
import pygame
from src.Model.SettingModel import ManiaSetting
import ast


class ConfigParser:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('././config.cfg', encoding='utf-8')

    def init_mania_setting(self, mania_setting: ManiaSetting):
        # hc
        _4key = self.config.get('KeyBind', '4k').split(',')
        _5key = self.config.get('KeyBind', '5k').split(',')
        _6key = self.config.get('KeyBind', '6k').split(',')
        _7key = self.config.get('KeyBind', '7k').split(',')
        _8key = self.config.get('KeyBind', '8k').split(',')
        _9key = self.config.get('KeyBind', '9k').split(',')

        for i in range(4, 10):
            mania_setting.keyBindDict[i] = []

        for keycode in _4key:
            mania_setting.keyBindDict[4].append(pygame.key.key_code(keycode))
        for keycode in _5key:
            mania_setting.keyBindDict[5].append(pygame.key.key_code(keycode))
        for keycode in _6key:
            mania_setting.keyBindDict[6].append(pygame.key.key_code(keycode))
        for keycode in _7key:
            mania_setting.keyBindDict[7].append(pygame.key.key_code(keycode))
        for keycode in _8key:
            mania_setting.keyBindDict[8].append(pygame.key.key_code(keycode))
        for keycode in _9key:
            mania_setting.keyBindDict[9].append(pygame.key.key_code(keycode))

        # ui
        mania_setting.noteSize = max(1, ast.literal_eval(self.config.get('Skin', 'noteSize')))
        mania_setting.lineWidth = max(1, ast.literal_eval(self.config.get('Skin', 'lineWidth')))
        mania_setting.hitPosition = ast.literal_eval(self.config.get('Skin', 'hitPosition'))
        mania_setting.judgementPosition = ast.literal_eval(self.config.get('Skin', 'judgementPosition'))
        mania_setting.comboPosition = ast.literal_eval(self.config.get('Skin', 'comboPosition'))
        mania_setting.noteColor = ast.literal_eval(self.config.get('Skin', 'noteColor'))
        mania_setting.lnBodyColor = ast.literal_eval(self.config.get('Skin', 'lnBodyColor'))

        # 预防bug
        if mania_setting.noteSize > mania_setting.lineWidth:
            mania_setting.lineWidth = mania_setting.noteSize + 20
        if not self.is_valid_color(mania_setting.noteColor):
            mania_setting.noteColor = (255, 121, 174)
        if not self.is_valid_color(mania_setting.lnBodyColor):
            mania_setting.lnBodyColor = (117, 117, 120)

    def is_valid_color(self, color):
        if not isinstance(color, tuple):
            return False
        if len(color) != 3:
            return False
        for value in color:
            if not isinstance(value, int) or not (0 <= value <= 255):
                return False
        return True
