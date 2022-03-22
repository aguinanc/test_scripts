import numpy as _np
import time as _time
from epics import caget, caput

NUMBER_OF_CYCLES = 500

DELAY_ADJUST = 0.2
DELAY_POINT = 3.0
DELAY_WAIT = 2.0
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

# Not mirror mode
## Phase: CSE + CID
## Counterphase: CSE + CID
## GV: CSE + CSD
## GH: CSE + CIE

# Init motion param lists

init_delay_list = [
        DELAY_POINT,
        DELAY_POINT,
        DELAY_POINT,
        ]

init_pos_list = [
        0.0,
        13.125,
        -26.25,
        ]

init_mode_list = [
        'GV',
        'Phase',
        'GV',
        ]

# Cycle motion param lists

delay_list = [
        DELAY_WAIT,
        DELAY_POINT,
        DELAY_POINT,
        DELAY_WAIT,
        DELAY_POINT,
        DELAY_POINT,
        ]

pos_list = [
        0.0,
        -13.125,
        26.25,
        0.0,
        13.125,
        -26.25,
        ]

mode_list = [
        'GV',
        'Phase',
        'GV',
        'GV',
        'Phase',
        'GV',
        ]

def pos_diff(mode, target):
    # get right readback
    if mode == couplings['All']:
        pos_mon = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['Phase']:
        pos_mon = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['Counterphase']:
        pos_mon = (-1) * caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['GV']:
        pos_mon = caget('delta:mod01:CSDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['GH']:
        pos_mon = caget('delta:mod01:CIEPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CSD']:
        pos_mon = caget('delta:mod01:CSDPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CSE']:
        pos_mon = caget('delta:mod01:CSEPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CIE']:
        pos_mon = caget('delta:mod01:CIEPhyPos-Mon', use_monitor=False)
    elif mode == couplings['CID']:
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

def move_abs(mode, pos):
    relpos = pos_diff(mode, pos)
    move_rel(relpos)

# do initial motion to position device
for i in range(0, len(init_pos_list)):
    print('---  Moving to initial position  ---')
    # configure coupling
    coup = couplings[init_mode_list[i]]
    caput('delta:mod01:Coup-Sel', coup, wait=True)
    _time.sleep(DELAY_ADJUST)
    # start move
    move_abs(coup, init_pos_list[i])
    # wait move to finish
    _time.sleep(init_delay_list[i])

# let user know that init is finished
cse_pos = caget('delta:mod01:CSEPhyPos-Mon', use_monitor=False)
csd_pos = caget('delta:mod01:CSDPhyPos-Mon', use_monitor=False)
cie_pos = caget('delta:mod01:CIEPhyPos-Mon', use_monitor=False)
cid_pos = caget('delta:mod01:CIDPhyPos-Mon', use_monitor=False)
print('  Initial position:')
print('  CSE: {0} mm'.format(cse_pos))
print('  CSD: {0} mm'.format(csd_pos))
print('  CIE: {0} mm'.format(cie_pos))
print('  CID: {0} mm'.format(cid_pos))

# wait for user command
input("Press Enter to start test")

# do cycle NUMBER_OF_CYCLE times
for i in range(0, NUMBER_OF_CYCLES):
    print('---  Cycle {0}/{1}  ---'.format(i+1, NUMBER_OF_CYCLES))
    for i in range(0, len(pos_list)):
        print('  coupling = {0}'.format(mode_list[i]))
        print('  target = {0}'.format(pos_list[i]))
        coup = couplings[mode_list[i]]
        # configure coupling
        caput('delta:mod01:Coup-Sel', coup, wait=True)
        _time.sleep(DELAY_ADJUST)
        # start move
        move_abs(coup, pos_list[i])
        # wait move to finish
        _time.sleep(delay_list[i])
print('---  Test finished  ---')

