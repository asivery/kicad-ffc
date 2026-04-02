import sys
import os
sys.path.append(os.path.join(sys.path[0], "kicad-footprint-generator"))

from KicadModTree import *



from dataclasses import dataclass, field
from typing import List, Callable, Optional

@dataclass
class BallEntry:
    name: str = ''
    dimensions: (float, float) = (0, 0)
    ballcount: float= 0
    pitch: float = 0
    diameter: float = 0
    number_func: Callable[float, float, str] = None
    ballmatrix: List[List[int]] = field(default_factory=list)


@dataclass
class BallResult:
    entries: List[BallEntry] = field(default_factory=list)

def parse_property_line(line: str, expect_name: Optional[str] = None) -> (str, str):
    space = line.find(' ')
    if space == -1:
        raise BaseException(f"Tried to parse property line{f' (forced {expect_name})' if expect_name else ''}")
    name, value = line[:space], line[space+1:]
    name = name.strip()
    value = value.strip()
    if expect_name is not None and name != expect_name:
        raise BaseException(f"Expected property {expect_name}, got {name}")
    return name, value

def discard_empty_lines(lines: List[str]):
    while len(lines) and lines[0] == '': lines.pop(0)

def parse_dimensions(value: str) -> (float, float):
    vals = value.split('x')
    if len(vals) != 2: raise BaseException('Invalid amount of dimensions!')
    return float(vals[0]), float(vals[1])

def parse_entry(lines: List[str]) -> BallEntry:
    entry = BallEntry()
    while lines[0] != '':
        name, value = parse_property_line(lines.pop(0))
        if name == 'name':
            entry.name = value
        elif name == 'dimensions':
            entry.dimensions = parse_dimensions(value)
        elif name == 'ballcount':
            entry.ballcount = int(value)
        elif name == 'pitch':
            entry.pitch = float(value)
        elif name == 'diameter':
            entry.diameter = float(value)
        elif name == 'number':
            entry.number_func = eval(value)
        else:
            raise BaseException(f'Unknown entry property {name}')
    lines.pop(0)
    entry.ballmatrix = parse_ball_matrix(lines)
    return entry

def parse_ball_matrix(lines: List[str]) -> List[List[int]]:
    rows = []
    while lines[0] != '':
        rows.append([int(x) for x in lines.pop(0) if x in '01'])
    return rows

def parse_module(lines: List[str]) -> BallResult:
    discard_empty_lines(lines)
    module = BallResult()

    while len(lines):
        module.entries.append(parse_entry(lines))
        discard_empty_lines(lines)
    return module


with open(sys.argv[1], 'r') as e:
    textcontent = [x.strip() for x in e.read().split('\n')]
module = parse_module(textcontent)


for entry in module.entries:
    ftp = Footprint(entry.name)
    ftp.append(Line(start=[entry.dimensions[0] / -2, entry.dimensions[1] / -2], end=[entry.dimensions[0] / -2, entry.dimensions[1] / 2]))
    ftp.append(Line(start=[entry.dimensions[0] / -2, entry.dimensions[1] / 2], end=[entry.dimensions[0] / 2, entry.dimensions[1] / 2]))
    ftp.append(Line(start=[entry.dimensions[0] / 2, entry.dimensions[1] / 2], end=[entry.dimensions[0] / 2, entry.dimensions[1] / -2]))
    ftp.append(Line(start=[entry.dimensions[0] / 2, entry.dimensions[1] / -2], end=[entry.dimensions[0] / -2, entry.dimensions[1] / -2]))

    position_y = (len(entry.ballmatrix) / -2) * entry.pitch + entry.pitch/2
    c = 0
    for row in range(len(entry.ballmatrix)):
        position_x = (len(entry.ballmatrix[0]) / -2) * entry.pitch + entry.pitch/2
        for column in range(len(entry.ballmatrix[0])):
            if entry.ballmatrix[row][column]:
                c += 1
                ftp.append(Pad(
                    number = entry.number_func(column, row),
                    type = Pad.TYPE_SMT,
                    shape = Pad.SHAPE_CIRCLE,
                    at = [position_x, position_y],
                    size = entry.diameter,
                    layers = ['F.Cu']
                ))
            position_x += entry.pitch
        position_y += entry.pitch
    assert c == entry.ballcount
    ftp.append(Text(
        type='value', text=entry.name, at=[0, entry.dimensions[1] / 2 + 2], layer='F.SilkS'
    ))
    ftp.append(Text(
        type='reference', text='REF**', at=[0, entry.dimensions[1] / 2 + 4], layer='F.SilkS'
    ))

    out_mod = KicadFileHandler(ftp)
    out_mod.writeFile(entry.name + '.kicad_mod')

