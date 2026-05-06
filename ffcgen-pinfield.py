import sys
import os
sys.path.append(os.path.join(sys.path[0],"kicad-footprint-generator"))

from KicadModTree import *

COLUMNS = 100
ROWS = 70
PITCH = 2.54
NAME = f"PINFIELD {COLUMNS}x{ROWS} pins, {PITCH}mm pitch"
FILENAME = f"PINFIELD{COLUMNS}x{ROWS}_{PITCH}.kicad_mod"
PAD_SIZE = 1.65
DRILL = 0.8

kicad_mod = Footprint(NAME)

position_x = 0
for i in range(ROWS):
    kicad_mod.append(PadArray(start=[0, PITCH*i], initial=COLUMNS*i+1,
        pincount=COLUMNS, increment=1,  x_spacing=PITCH, size=PAD_SIZE,
        type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, layers=Pad.LAYERS_THT, drill=DRILL))

file_handler = KicadFileHandler(kicad_mod)
file_handler.writeFile(FILENAME)
