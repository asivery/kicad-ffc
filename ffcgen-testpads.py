import sys
import os
sys.path.append(os.path.join(sys.path[0],"kicad-footprint-generator"))

from KicadModTree import *

PINCOUNT = 10
PITCH = 3
NAME = f"TESTPAD {PINCOUNT} pins, {PITCH}mm pitch"
FILENAME = f"TESTPAD{PINCOUNT}_{PITCH}.kicad_mod"
PAD_SIZE = 2

kicad_mod = Footprint(NAME)

position_x = 0
kicad_mod.append(PadArray(start=[0, 0], initial=1,
    pincount=PINCOUNT, increment=1,  x_spacing=PITCH, size=PAD_SIZE,
    type=Pad.TYPE_SMT, shape=Pad.SHAPE_CIRCLE, layers=Pad.LAYERS_SMT))

file_handler = KicadFileHandler(kicad_mod)
file_handler.writeFile(FILENAME)
