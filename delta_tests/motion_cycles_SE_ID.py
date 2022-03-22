import numpy as _np
import time as _time
from epics import caget, caput

MAX_FWD_POS = 26.25
MAX_BKW_POS = -26.25

INITIAL_POS = 0.0

NUMBER_OF_CYCLES = 500

DELAY_ADJUST = 0.2
DELAY_POINT = 3.0
DELAY_LIST = 2.0
DELAY_BEFORE_CYCLE = 3.0
DELAY_AFTER_CONFIG = 1.0

couplings = {
        'None': 0,
        'All': 1,
        'Phase': 2,
        'Counterphase': 3,
        'GV': 4,
        'GH': 5,
        'CSD': 6,
        'CSE': 7,
        'CIE': 8,
        'CID': 9,
        }

mirror_config = {
        'Normal': 0,
        'Mirror': 1,
        }

mode = couplings['Phase']
mirror_mode = mirror_config['Normal']
step = 1
back_step = step*(-1)

# Not mirror mode
## Phase: CSE + CID
## Counterphase: CSE + CID
## GV: CSE + CSD
## GH: CSE + CIE

# Mirror mode
## Phase: CSD + CIE
## Counterphase: CSD + CIE
## GV: CIE + CID
## GH: CSD + CID

# Position lists

# go forward in steps
#pos_list_1 = _np.arange(INITIAL_POS+step, MAX_FWD_POS+step, step)
pos_list_1 = [MAX_FWD_POS]
# return to start in steps
#pos_list_2 = _np.arange(MAX_FWD_POS+back_step, INITIAL_POS+back_step, back_step)
pos_list_2 = [INITIAL_POS]
# go backwards in steps
#pos_list_3 = _np.arange(INITIAL_POS+back_step, MAX_BKW_POS+back_step, back_step)
pos_list_3 = [MAX_BKW_POS]
# return to start in steps
#pos_list_4 = _np.arange(MAX_BKW_POS+step, INITIAL_POS+step, step)
pos_list_4 = [INITIAL_POS]

def pos_diff(mode, mirror, target):
    # get readback
    if mode == couplings['All']:
        pos_mon = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CSD']:
        pos_mon = caget('delta:mod01:CSDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CSE']:
        pos_mon = caget('delta:mod01:CSEPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CIE']:
        pos_mon = caget('delta:mod01:CIEPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CID']:
        pos_mon = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    # Not mirror mode
    elif mode == couplings['Phase'] and mirror == False:
        pos_mon = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['Counterphase'] and mirror == False:
        pos_mon = (-1) * caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['GV'] and mirror == False:
        pos_mon = caget('delta:mod01:CSDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['GH'] and mirror == False:
        pos_mon = caget('delta:mod01:CIEPhyPos-Mon', use_monitor=False)
    # Mirror mode
    elif mode == couplings['Phase'] and mirror == True:
        pos_mon = caget('delta:mod01:CIEPhyPos-Mon', use_monitor=False)
    elif mode == couplings['Counterphase'] and mirror == True:
        pos_mon = (-1) * caget('delta:mod01:CIEPhyPos-Mon', use_monitor=False)
    elif mode == couplings['GV'] and mirror == True:
        pos_mon = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['GH'] and mirror == True:
        pos_mon = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    return target - pos_mon

def move_rel(relpos):
    caput('delta:mod01:Stop-Cmd', 1, wait=True)
    _time.sleep(DELAY_ADJUST)
    caput('delta:mod01:RelPos-SP', relpos, wait=True)
    _time.sleep(DELAY_ADJUST)
    caput('delta:mod01:Rst-Cmd', 1, wait=True)
    _time.sleep(DELAY_ADJUST)
    caput('delta:mod01:SoftTrig-Cmd', 1, wait=True)
    _time.sleep(DELAY_ADJUST)

def move_abs(mode, mirror, pos):
    relpos = pos_diff(mode, mirror, pos)
    move_rel(relpos)

# do cycle NUMBER_OF_CYCLE times
for i in range(0, NUMBER_OF_CYCLES):
    # configure coupling
    caput('delta:mod01:Coup-Sel', mode, wait=True)
    # configure mirror mode
    mirror = mirror_mode
    caput('delta:mod01:Mirror-Sel', mirror_mode)
    _time.sleep(DELAY_ADJUST)
    _time.sleep(DELAY_AFTER_CONFIG)
    # move to start position
    pos = INITIAL_POS
    move_abs(mode, mirror, pos)
    _time.sleep(DELAY_BEFORE_CYCLE)
    # execute first position list
    print('-- New cycle start --')
    for p in pos_list_1:
        move_abs(mode, mirror, p)
        print('  Moving to {}'.format(p))
        _time.sleep(DELAY_POINT)
    _time.sleep(DELAY_LIST)
    for p in pos_list_2:
        move_abs(mode, mirror, p)
        print('  Moving to {}'.format(p))
        _time.sleep(DELAY_POINT)
    _time.sleep(DELAY_LIST)
    for p in pos_list_3:
        move_abs(mode, mirror, p)
        print('  Moving to {}'.format(p))
        _time.sleep(DELAY_POINT)
    _time.sleep(DELAY_LIST)
    for p in pos_list_4:
        move_abs(mode, mirror, p)
        print('  Moving to {}'.format(p))
        _time.sleep(DELAY_POINT)
    _time.sleep(DELAY_LIST)
    print('Cycle {} finished'.format(i+1))

