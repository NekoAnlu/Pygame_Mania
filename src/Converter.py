import json
import os
import sys
from Model.BeatmapModel import *


class MCConverter:
    @staticmethod
    def mc_pre_converter(root_path: str) -> Song:
        _chartFile = []
        song = Song()
        song.charts = []
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith('.mc'):
                    _chartFile.append(os.path.join(root, file))

        # 先读取其中一个chart获取基本信息
        with open(_chartFile[0], 'r') as file:
            data = json.load(file)
            # 歌曲基本信息
            song.title = data['meta']['song']['title']
            song.artist = data['meta']['song']['artist']
            if 'titleorg' in data['meta']['song']:
                song.titleOrg = data['meta']['song']['titleorg']
            if 'artistorg' in data['meta']['song']:
                song.artistOrg = data['meta']['song']['artistorg']

        # 读取所有mc拿到除按键外所有信息
        for filepath in _chartFile:
            chart = Chart()
            with open(filepath, 'r') as file:
                data = json.load(file)
                _basepath = filepath[0:filepath.rfind('\\') + 1]
                # 跳过非mania的chart
                if data['meta']['mode'] != 0:
                    continue

                # 谱面数据
                _bpmData = data['time']
                _noteData = data['note']

                chart.creator = data['meta']['creator']
                chart.backgroundPath = _basepath + data['meta']['background']  # temp3
                chart.version = data['meta']['version']
                chart.columnNum = data['meta']['mode_ext']['column']
                if 'preview' in data['meta']:
                    chart.previewTime = data['meta']['preview']
                chart.filePath = filepath  # temp
                chart.audioPath = _basepath + _noteData[-1]['sound']  # temp2
                if 'offset' in _noteData[-1]:
                    chart.offset = _noteData[-1]['offset']
                else:
                    chart.offset = 0
                chart.noteNum = len(_noteData) - 1

                chart.bpmList = []
                chart.bpmList.append((_bpmData[0]["bpm"], 0))

            song.charts.append(chart)

        return song

    @staticmethod
    def mc_converter(path: str) -> Song:
        song = Song()
        chart = Chart()
        
        with open(path, 'r') as file:
            data = json.load(file)
            _basepath = path[0:path.rfind('\\')+1]
            # 歌曲基本信息
            song.title = data['meta']['song']['title']
            song.artist = data['meta']['song']['artist']
            if 'titleorg' in data['meta']['song']:
                song.titleOrg = data['meta']['song']['titleorg']
            if 'artistorg' in data['meta']['song']:
                song.artistOrg = data['meta']['song']['artistorg']

            # 谱面数据
            _bpmData = data['time']
            _noteData = data['note']

            # 谱面基本信息
            chart.creator = data['meta']['creator']
            chart.backgroundPath = _basepath + data['meta']['background']  # temp3
            chart.version = data['meta']['version']
            chart.columnNum = data['meta']['mode_ext']['column']
            if 'preview' in data['meta']:
                chart.previewTime = data['meta']['preview']
            # chart.filePath = filepath  # temp
            chart.audioPath = _basepath + _noteData[-1]['sound']  # temp2
            if 'offset' in _noteData[-1]:
                chart.offset = _noteData[-1]['offset']
            else:
                chart.offset = 0
            chart.noteNum = len(_noteData) - 1
            _noteData.pop()  # 删掉最后一个note

            # 单bpm
            chart.bpmList = []
            chart.bpmList.append((_bpmData[0]["bpm"], 0))

            # 多bpm处理
            if len(_bpmData) > 1:
                _lastBpm = chart.bpmList[0][0]
                _lastBpmTiming = -1
                for i, _bpm in enumerate(_bpmData):
                    if i == 0:
                        continue  #跳过处理过的0
                    _currBpm = _bpm['bpm']
                    _lastSpb = float(60) / _lastBpm
                    _lastBeat = (_bpmData[i - 1]["beat"][0], _bpmData[i - 1]["beat"][1], _bpmData[i - 1]["beat"][2])
                    _currBeat = (_bpmData[i]["beat"][0], _bpmData[i]["beat"][1], _bpmData[i]["beat"][2])
                    if i == 1:
                        _timing = _lastSpb * ((_currBeat[0] - _lastBeat[0]) + ((_currBeat[1] / _currBeat[2]) - (_lastBeat[1] / _lastBeat[2]))) * 1000 - chart.offset
                    else:
                        _timing = _lastBpmTiming + _lastSpb * ((_currBeat[0] - _lastBeat[0]) + ((_currBeat[1] / _currBeat[2]) - (_lastBeat[1] / _lastBeat[2]))) * 1000
                    _lastBpmTiming = _timing
                    _lastBpm = _currBpm
                    chart.bpmList.append((_currBpm, _timing))

            # 按键信息
            chart.noteList = []
            # 单bpm
            if len(chart.bpmList) == 1:
                _bpm = chart.bpmList[0][0]
                _spb = float(60) / _bpm
                for _note in _noteData:
                    note = Note()
                    _beat = (_note['beat'][0], _note['beat'][1], _note['beat'][2])
                    note.startTiming = (_beat[0] * _spb + _spb / _beat[2] * _beat[1]) * 1000 - chart.offset

                    # 判断LN
                    if 'endbeat' in _note:
                        _endBeat = (_note['endbeat'][0], _note['endbeat'][1], _note['endbeat'][2])
                        note.endTiming = (_endBeat[0] * _spb + _spb / _endBeat[2] * _endBeat[1]) * 1000 - chart.offset
                        note.noteType = 1
                    else:
                        note.noteType = 0

                    note.line = _note["column"]
                    chart.noteList.append(note)

            # 变速
            else:
                _currBpmIndex = 0
                for _note in _noteData:
                    note = Note()
                    _noteBeat = (_note['beat'][0], _note['beat'][1], _note['beat'][2])
                    note.startTiming = MCConverter._mc_calculate_svtiming(_bpmData, chart, _currBpmIndex, _noteBeat)

                    if 'endbeat' in _note:
                        _endBeat = (_note['endbeat'][0], _note['endbeat'][1], _note['endbeat'][2])
                        note.endTiming = MCConverter._mc_calculate_svtiming(_bpmData, chart, _currBpmIndex, _endBeat)
                        note.noteType = 1
                    else:
                        note.noteType = 0

                    note.line = _note["column"]
                    chart.noteList.append(note)

            song.charts = [chart]

            return song

    @staticmethod
    def _mc_calculate_svtiming(_bpmData, chart: Chart, _currBpmIndex, _noteBeat) -> float:
        _currBpmBeat = (_bpmData[_currBpmIndex]['beat'][0], _bpmData[_currBpmIndex]['beat'][1], _bpmData[_currBpmIndex]['beat'][2])
        _nextBpmBeat = _currBpmBeat
        _currBpm = _bpmData[_currBpmIndex]["bpm"]
        _currSpb = float(60) / _currBpm
        _currBeatTime = _noteBeat[0] + float(_noteBeat[1]) / _noteBeat[2]
        _nextBeatTime = -1
        _timing = -1
        if _currBpmIndex < len(chart.bpmList) - 1:
            _nextBpmBeat = (_bpmData[_currBpmIndex + 1]['beat'][0], _bpmData[_currBpmIndex + 1]['beat'][1],
                            _bpmData[_currBpmIndex + 1]['beat'][2])
            _nextBeatTime = _nextBpmBeat[0] + float(_nextBpmBeat[1]) / _nextBpmBeat[2]
        else:
            _nextBeatTime = sys.maxsize

        if _currBpmIndex == 0:
            _timing = (_noteBeat[0] * _currSpb + _currSpb * _noteBeat[1] / _noteBeat[2]) * 1000 - chart.offset
        else:
            _timing = chart.bpmList[_currBpmIndex][1] + _currSpb * ((_noteBeat[0] - _currBpmBeat[0]) + (
                        (_noteBeat[1] / _noteBeat[2]) - (_currBpmBeat[1] / _currBpmBeat[2]))) * 1000

        while _currBpmIndex < len(chart.bpmList) - 1 and _currBeatTime >= _nextBeatTime:
            _currBpmIndex += 1
            _currBpmBeat = _nextBpmBeat
            if _currBpmIndex < len(chart.bpmList) - 1:
                _nextBpmBeat = (_bpmData[_currBpmIndex + 1]['beat'][0], _bpmData[_currBpmIndex + 1]['beat'][1],
                                _bpmData[_currBpmIndex + 1]['beat'][2])
                _nextBeatTime = _nextBpmBeat[0] + float(_nextBpmBeat[1]) / _nextBpmBeat[2]
            else:
                _nextBeatTime = sys.maxsize
            _currBpm = _bpmData[_currBpmIndex]["bpm"]
            _currSpb = float(60) / _currBpm
            _timing = chart.bpmList[_currBpmIndex][1] + _currSpb * ((_noteBeat[0] - _currBpmBeat[0]) + (
                        (_noteBeat[1] / _noteBeat[2]) - (_currBpmBeat[1] / _currBpmBeat[2]))) * 1000

        return _timing


# c = MCConverter()
# c.mc_converter('1')
