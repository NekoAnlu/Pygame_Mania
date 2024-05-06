import configparser
import pygame
from src.Model.SettingModel import ManiaSetting
import ast


class ConfigParser:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

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
        mania_setting.noteSize = ast.literal_eval(self.config.get('Skin', 'noteSize'))
        mania_setting.lineWidth = ast.literal_eval(self.config.get('Skin', 'lineWidth'))
        mania_setting.judgementPosition = ast.literal_eval(self.config.get('Skin', 'judgementPosition'))
        mania_setting.comboPosition = ast.literal_eval(self.config.get('Skin', 'comboPosition'))
        mania_setting.noteColor = ast.literal_eval(self.config.get('Skin', 'noteColor'))
        print(mania_setting.noteColor)
