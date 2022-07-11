import time
import numpy as np
from epics import caput, caget

NUM_CYCLES = 200
DELAY_BETWEEN_MOVES = 4 # seg
POS_PV = 'vac-test:galil:AbsPos-SP'
MON_PV = 'vac-test:galil:EncPos-Mon'

# Positions
START_POS = 12.85
MID_POS = 14.5
END_POS = 17.55

TOL = 0.01 # mm

OUT_FILE = 'scrap_error_output.txt'

for i in range(0, NUM_CYCLES):
    print('Cycle #{}'.format(i))
    caput(POS_PV, START_POS)
    time.sleep(DELAY_BETWEEN_MOVES)
    rbv = caget(MON_PV)
    if np.abs(rbv - START_POS) > TOL:
        with open(OUT_FILE, 'a') as f:
            f.write('{}: Error moving to {}, got only to {}'.format(time.ctime(), START_POS, rbv))
            f.write('\n')
    caput(POS_PV, MID_POS)
    time.sleep(DELAY_BETWEEN_MOVES)
    rbv = caget(MON_PV)
    if np.abs(rbv - MID_POS) > TOL:
        with open(OUT_FILE, 'a') as f:
            f.write('{}: Error moving to {}, got only to {}'.format(time.ctime(), MID_POS, rbv))
            f.write('\n')
    caput(POS_PV, END_POS)
    time.sleep(DELAY_BETWEEN_MOVES)
    rbv = caget(MON_PV)
    if np.abs(rbv - END_POS) > TOL:
        with open(OUT_FILE, 'a') as f:
            f.write('{}: Error moving to {}, got only to {}'.format(time.ctime(), END_POS, rbv))
            f.write('\n')
    caput(POS_PV, MID_POS)
    time.sleep(DELAY_BETWEEN_MOVES)
    rbv = caget(MON_PV)
    if np.abs(rbv - MID_POS) > TOL:
        with open(OUT_FILE, 'a') as f:
            f.write('{}: Error moving to {}, got only to {}'.format(time.ctime(), MID_POS, rbv))
            f.write('\n')

