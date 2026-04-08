from __future__ import annotations

from pathlib import Path
from typing import NamedTuple


class Area(NamedTuple):
    # start offset is inclusive and end offset is exclusive!
    start: int
    end: int

    def __str__(self):
        return f'({self.start}:{self.end})'

    def __repr__(self):
        return self.__str__()


class CarvingArea:
    def __init__(self, size: int):
        self.uncarved_areas: list[Area] = [Area(0, size)]

    def add_carved_area(self, carved_area: Area) -> None:
        areas = self.uncarved_areas
        self.uncarved_areas = []
        for uncarved_area in areas:
            if uncarved_area.end <= carved_area.start or carved_area.end <= uncarved_area.start:
                # uncarved area before _______XXXXXX_  or _XXXXXX_________
                # carved area          _YYYY_________  or __________YYYYY_
                # uncarved area after  _______XXXXXX_  or _XXXXXX_________
                self.uncarved_areas.append(uncarved_area)
            elif carved_area.start <= uncarved_area.start and uncarved_area.end <= carved_area.end:
                # uncarved area before _____XXXXXXXX______
                # carved area          ____YYYYYYYYYY_____
                # uncarved area after  ___________________
                continue
            elif uncarved_area.start < carved_area.start and uncarved_area.end <= carved_area.end:
                # uncarved area before _____XXXXXXXX______
                # carved area          ________YYYYYYY____
                # uncarved area after  _____XXX___________
                self.uncarved_areas.append(Area(uncarved_area.start, carved_area.start))
            elif carved_area.start <= uncarved_area.start and carved_area.end < uncarved_area.end:
                # uncarved area before _____XXXXXXXX______
                # carved area          ___YYYYYY__________
                # uncarved area after  _________XXXX______
                self.uncarved_areas.append(Area(carved_area.end, uncarved_area.end))
            elif uncarved_area.start < carved_area.start and carved_area.end < uncarved_area.end:
                # uncarved area before ____XXXXXXXXXXX____
                # carved area          _______YYYYY_______
                # uncarved area after  ____XXX_____XXX____
                self.uncarved_areas.append(Area(uncarved_area.start, carved_area.start))
                self.uncarved_areas.append(Area(carved_area.end, uncarved_area.end))
            else:
                raise Exception('Carving error')

    def __str__(self):
        return ' '.join(str(area) for area in self.uncarved_areas)


class Carver:
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.file_size = self.filepath.stat().st_size
        self.carved = CarvingArea(self.file_size)

    def extract_data(self, start: int, end: int | None = None) -> bytes:
        with self.filepath.open('rb') as opened_file:
            opened_file.seek(start)

            if end is not None:
                self.carved.add_carved_area(Area(start, end))
                return opened_file.read(end - start)
            else:
                self.carved.add_carved_area(Area(start, self.file_size))
                return opened_file.read()
