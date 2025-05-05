import sys
import os
sys.path.append(os.path.join(sys.path[0], "kicad-footprint-generator"))

from KicadModTree import *

PINCOUNT_TOP = 13
PINCOUNT_BOTTOM = 12
PITCH = 0.3
SIZE_BOTTOM = (0.4, 1.2)
SIZE_TOP = (0.4, 1.2)
SPACING_TOP_BOTTOM = 0
CHAMFER_SIZE = 0.15
BOTTOM_LEADOUT_HEIGHT = 0.3
DISTANCE_BETWEEN_PADS = 2*PITCH - SIZE_BOTTOM[0]
LEADOUT_WIDTH = SIZE_BOTTOM[0] - 2*CHAMFER_SIZE
TOP_LEADOUT_HEIGHT = BOTTOM_LEADOUT_HEIGHT + SIZE_BOTTOM[1]
def offset_all(nodes, by):
    return [(n[0] + by[0], n[1] + by[1]) for n in nodes]


DISTANCE_BETWEEN_ADJ = CHAMFER_SIZE / 2

BOTTOM_PRIMITIVES = [
    Polygon(nodes=offset_all([
        (CHAMFER_SIZE, -DISTANCE_BETWEEN_ADJ), # Top, left - start of the "top-leg" / chamfer
        (CHAMFER_SIZE, -SIZE_TOP[1]), # top leg top left
        (SIZE_BOTTOM[0] - CHAMFER_SIZE, -SIZE_TOP[1]), # top leg top right
        (SIZE_BOTTOM[0] - CHAMFER_SIZE, 0-DISTANCE_BETWEEN_ADJ), # before chamfer, top right
        (SIZE_BOTTOM[0], CHAMFER_SIZE-DISTANCE_BETWEEN_ADJ), # Chamfer, top right, start of pad
        
        (SIZE_BOTTOM[0], SIZE_BOTTOM[1] - CHAMFER_SIZE), # Pad - bottom right before chamfer
        (SIZE_BOTTOM[0] - CHAMFER_SIZE, SIZE_BOTTOM[1]), # Pad - bottom right - before leadout leg
        (SIZE_BOTTOM[0] - CHAMFER_SIZE, SIZE_BOTTOM[1] + BOTTOM_LEADOUT_HEIGHT), # bottom right, leadout leg
        (CHAMFER_SIZE, SIZE_BOTTOM[1] + BOTTOM_LEADOUT_HEIGHT), # bottom left, leadout leg
        (CHAMFER_SIZE, SIZE_BOTTOM[1]), # Start of bottom left pad chamfer
        (0, SIZE_BOTTOM[1] - CHAMFER_SIZE), # End of bottom left pad chamfer
        (0, CHAMFER_SIZE -DISTANCE_BETWEEN_ADJ), # Top left end of chamfer
        (CHAMFER_SIZE, -DISTANCE_BETWEEN_ADJ), # top rights tart of chamfer
    ], (-LEADOUT_WIDTH / 2 - (SIZE_BOTTOM[0] - LEADOUT_WIDTH) / 2, -BOTTOM_LEADOUT_HEIGHT*0.5 - SIZE_BOTTOM[1])))
]

TOP_PRIMITIVES = [
    Polygon(nodes=offset_all([
        (0, 0), # Top, left
        (SIZE_TOP[0], 0), # Top right
        
        (SIZE_TOP[0], SIZE_TOP[1] - CHAMFER_SIZE + DISTANCE_BETWEEN_ADJ), # Bottom right
        (SIZE_TOP[0] - CHAMFER_SIZE, SIZE_TOP[1] + DISTANCE_BETWEEN_ADJ), # chamfer, start of leadout leg, bottom right
        (SIZE_TOP[0] - CHAMFER_SIZE, SIZE_TOP[1] + TOP_LEADOUT_HEIGHT), # end of leadout leg, bottom right
        (CHAMFER_SIZE, SIZE_TOP[1] + TOP_LEADOUT_HEIGHT), # end of leadout leg, bottom left
        (CHAMFER_SIZE, SIZE_TOP[1] + DISTANCE_BETWEEN_ADJ), # Chamfer start, start of leadout leg, bottom left
        (0, SIZE_TOP[1] - CHAMFER_SIZE + DISTANCE_BETWEEN_ADJ), # Chamfer end, end of pad, bottom left
        (0, 0), # Top left
    ], (-LEADOUT_WIDTH / 2 - (SIZE_TOP[0] - LEADOUT_WIDTH) / 2, -TOP_LEADOUT_HEIGHT*0.5 - SIZE_TOP[1])))
]

NAME = f"FFC-stagger {PINCOUNT_TOP + PINCOUNT_BOTTOM} pins, {PITCH}mm pitch"
FILENAME = f"FFC{PINCOUNT_TOP + PINCOUNT_BOTTOM}_{PITCH}.kicad_mod"

kicad_mod = Footprint(NAME)

position_x = 0
# Generate bottoms
kicad_mod.append(PadArray(start=[0, 0], initial=1,
    pincount=PINCOUNT_TOP, increment=2,  x_spacing=PITCH * 2, size=(LEADOUT_WIDTH, TOP_LEADOUT_HEIGHT),
    type=Pad.TYPE_SMT, shape=Pad.SHAPE_CUSTOM, layers=Pad.LAYERS_SMT, primitives=TOP_PRIMITIVES, anchor_shape=Pad.ANCHOR_RECT))

kicad_mod.append(PadArray(start=[PITCH, SIZE_TOP[1]*0.5 + SPACING_TOP_BOTTOM], initial=2,
    pincount=PINCOUNT_BOTTOM, increment=2,  x_spacing=PITCH * 2, size=(LEADOUT_WIDTH, BOTTOM_LEADOUT_HEIGHT),
    type=Pad.TYPE_SMT, shape=Pad.SHAPE_CUSTOM, layers=Pad.LAYERS_SMT, primitives=BOTTOM_PRIMITIVES, anchor_shape=Pad.ANCHOR_RECT))


# Follow up with corner tops, then main tops


file_handler = KicadFileHandler(kicad_mod)
file_handler.writeFile(FILENAME)
