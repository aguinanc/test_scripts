#!/usr/bin/env python

########################### Run in python 2 ###########################

import numpy as np
import optparse
import time
import datetime

from epics import caget, caput

#### Parsing

# setup
parser = optparse.OptionParser()
parser.add_option('--s1', action="store", dest="start1", type="float", default=0, help="CTRL 1 start position")
parser.add_option('--s2', action="store", dest="start2", type="float", default=0, help="CTRL 2 start position")
parser.add_option('--e1', action="store", dest="end1", type="float", default=0, help="CTRL 1 end position")
parser.add_option('--e2', action="store", dest="end2", type="float", default=0, help="CTRL 2 end position")
parser.add_option('--cnt', action="store", dest="cnt", type="int", default=2, help="Track point count for both controllers")
parser.add_option('-j', action="store_true", default=False, help="Jump initialization")
parser.add_option('-d', action="store_true", default=False, help="Specify a given destination position index")
parser.add_option('--idx1', action="store", dest="arg_idx_1", type="int", default=0, help="CTRL 1 destination position index")
parser.add_option('--idx2', action="store", dest="arg_idx_2", type="int", default=0, help="CTRL 2 destination position index")
parser.add_option('-b', action="store_true", default=False, help="Move forward for the specified number of points and then the same backwards. Does not work when a destination is specified.")

# parse
(options, args) = parser.parse_args()

#### Variables

start_pos_1 = options.start1
end_pos_1 = options.end1
start_pos_2 = options.start2
end_pos_2 = options.end2
point_cnt = options.cnt

jump = options.j
specify_dest = options.d
dest_index_1 = options.arg_idx_1
dest_index_2 = options.arg_idx_2
backwards = options.b

# get date and time string
time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

#### Constants

P_CTRL_1 = 'galil1:' # bottow
P_CTRL_2 = 'galil2:' # top

CTRL_1_POS = P_CTRL_1 + 'Mtr.VAL'
CTRL_2_POS = P_CTRL_2 + 'Mtr.VAL'

CONFIG_DELAY = 0.5

CTRL_1_RB = P_CTRL_1 + 'EncPos-Mon'
CTRL_2_RB = P_CTRL_2 + 'EncPos-Mon'

LOG_FILE_1 = "ctrl_1_"+time_str
LOG_FILE_2 = "ctrl_2_"+time_str

# general config

AMP_GAIN = 0
LIMSW_TYPE = 0 # NO
MTR_TYPE = 3 # LA Stepper
AMPCURR_GAIN = 0
LOWCURR = 1
MTR_RES = 0.000009765625
MTR_SREV = 51200
VMAX = 1
VELO = 1
ACC = 2
NTM = 0
RETRY_CNT = 0
RETRY_DBD = 1
ENC_TYPE = 0 # normal quadrature
ENC_RES = 0.00005
UEIP = 1
BISS_IN = 1 # replace main
BISS_LVL = 0 # low low
BISS_POLL = 1
BISS_CLK = 9
BISS_NUMBITS1 = 33
BISS_NUMBITS2 = 33
BISS_ZEROPAD = 0

# galil 1 config

DIR_1 = 0 # pos
OFF_1 = 0

# galil 2 config

DIR_2 = 1 # neg
OFF_2 = 0

#### Procedure

print '##################################'
print '#  Scraper Position Measurement  #'
print '##################################'
print ' '

if jump:
    print 'X   X   X   X   X   X   X   X   X   X'
    print '  Jumping controller configuration'
    print 'X   X   X   X   X   X   X   X   X   X'
    print ' '
else:
    # configure controllers
    print '--> Configuring controllers 0 %' 
    print ' '
    caput(P_CTRL_1+'AmpEnbl-Sel', 0, wait=True)                      # turn amp off
    caput(P_CTRL_2+'AmpEnbl-Sel', 0, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'AmpGain-Sel', AMP_GAIN, wait=True)               # set amp gain
    caput(P_CTRL_2+'AmpGain-Sel', AMP_GAIN, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'LimSwType-Sel', LIMSW_TYPE, wait=True)           # set lim sw type
    caput(P_CTRL_2+'LimSwType-Sel', LIMSW_TYPE, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'MtrType-Sel', MTR_TYPE, wait=True)               # set motor type
    caput(P_CTRL_2+'MtrType-Sel', MTR_TYPE, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'AmpCurrLoopGain-Sel', AMPCURR_GAIN, wait=True)   # set amp curr loop gain
    caput(P_CTRL_2+'AmpCurrLoopGain-Sel', AMPCURR_GAIN, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'LowCurrMode-SP', LOWCURR, wait=True)             # set low curr mode
    caput(P_CTRL_2+'LowCurrMode-SP', LOWCURR, wait=True)
    time.sleep(CONFIG_DELAY)
    print ' '
    print '--> Configuring controllers 25 %'
    print ' '
    caput(P_CTRL_1+'Mtr.SREV', MTR_SREV, wait=True)           # set steps per rev
    caput(P_CTRL_2+'Mtr.SREV', MTR_SREV, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.MRES', MTR_RES, wait=True)            # set motor resolution
    caput(P_CTRL_2+'Mtr.MRES', MTR_RES, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.VMAX', VMAX, wait=True)               #  set max speed
    caput(P_CTRL_2+'Mtr.VMAX', VMAX, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.VELO', VELO, wait=True)               # set speed
    caput(P_CTRL_2+'Mtr.VELO', VELO, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.ACCL', ACC, wait=True)                # set acc
    caput(P_CTRL_2+'Mtr.ACCL', ACC, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.DIR', DIR_1, wait=True)               # set dir ctrl 1
    caput(P_CTRL_2+'Mtr.DIR', DIR_2, wait=True)               # set dir ctrl 2
    time.sleep(CONFIG_DELAY)
    print ' '
    print '--> Configuring controllers 50 %'
    print ' '
    caput(P_CTRL_1+'Mtr.OFF', OFF_1, wait=True)               # set offset ctrl 1
    caput(P_CTRL_2+'Mtr.OFF', OFF_2, wait=True)               # set offset ctrl 2
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.NTM', NTM, wait=True)                 # set ntm
    caput(P_CTRL_2+'Mtr.NTM', NTM, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.RTRY', RETRY_CNT, wait=True)          # set retry count
    caput(P_CTRL_2+'Mtr.RTRY', RETRY_CNT, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.RDBD', RETRY_DBD, wait=True)          # set retry deadband
    caput(P_CTRL_2+'Mtr.RDBD', RETRY_DBD, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'MainEncType-Sel', ENC_TYPE, wait=True)    # set enc type
    caput(P_CTRL_2+'MainEncType-Sel', ENC_TYPE, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.ERES', ENC_RES, wait=True)            # set enc res
    caput(P_CTRL_2+'Mtr.ERES', ENC_RES, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'Mtr.UEIP', UEIP, wait=True)               # set ueip
    caput(P_CTRL_2+'Mtr.UEIP', UEIP, wait=True)
    time.sleep(CONFIG_DELAY)
    print ' '
    print '--> Configuring controllers 75 %'
    print ' '
    caput(P_CTRL_1+'BiSSIn-Sel', BISS_IN, wait=True)                 # set biss input
    caput(P_CTRL_2+'BiSSIn-Sel', BISS_IN, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'BiSSLvl-Sel', BISS_LVL, wait=True)               # set biss lvl
    caput(P_CTRL_2+'BiSSLvl-Sel', BISS_LVL, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'BiSSPoll-Sel', BISS_POLL, wait=True)             # enbl biss poll
    caput(P_CTRL_2+'BiSSPoll-Sel', BISS_POLL, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'BiSSClkDiv-SP', BISS_CLK, wait=True)             # set biss clk
    caput(P_CTRL_2+'BiSSClkDiv-SP', BISS_CLK, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'BiSSNumBits1-SP', BISS_NUMBITS1, wait=True)      # set biss num bits 1
    caput(P_CTRL_2+'BiSSNumBits1-SP', BISS_NUMBITS1, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'BiSSNumBits2-SP', BISS_NUMBITS2, wait=True)      # set biss num bits 2
    caput(P_CTRL_2+'BiSSNumBits2-SP', BISS_NUMBITS2, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'BiSSNumZeroPad-SP', BISS_ZEROPAD, wait=True)     # set biss zero pad
    caput(P_CTRL_2+'BiSSNumZeroPad-SP', BISS_ZEROPAD, wait=True)
    time.sleep(CONFIG_DELAY)
    caput(P_CTRL_1+'AmpEnbl-Sel', 1, wait=True)                      # turn amp on
    caput(P_CTRL_2+'AmpEnbl-Sel', 1, wait=True)
    time.sleep(CONFIG_DELAY)
    print ' '
    print '--> Configuring controllers DONE'
    print ' '
    # move controllers to start position
    print '--> Moving controllers to start position'
    print ' '
    caput(CTRL_1_POS, start_pos_1, wait=True)
    caput(CTRL_2_POS, start_pos_2, wait=True)

# wait user input
raw_input('===> | Press <ENTER> to start measurements | ')
print ' '

# get move sequences
track_1 = np.linspace(start_pos_1, end_pos_1, point_cnt)
track_2 = np.linspace(start_pos_2, end_pos_2, point_cnt)

if specify_dest:
    # move to specified destination
    print '--> Moving CTRL 1 to specified destination'
    caput(CTRL_1_POS, track_1[dest_index_1], wait=True)
    print '--> Moving CTRL 2 to specified destination'
    caput(CTRL_2_POS, track_2[dest_index_2], wait=True)
    # wait user input
    raw_input('==> | Press <ENTER> to continue | ')
    print ' '
    # get position readbacks
    ctrl_1_rb = caget(CTRL_1_RB, as_string=True, timeout=10)
    ctrl_2_rb = caget(CTRL_2_RB, as_string=True, timeout=10)
    with open(LOG_FILE_1, 'a') as f1:
        f1.write(ctrl_1_rb+"\n")
    with open(LOG_FILE_2, 'a') as f2:
        f2.write(ctrl_2_rb+"\n")
elif backwards:
    # forward motion
    for i in range(0, point_cnt):
        # print msg
        print '--> Move count '+str(i+1)+' / '+str(point_cnt*2)
        print '---> Array position is '+str(i)
        print '---> Moving CTRL 1 to position '+str(track_1[i])
        print '---> Moving CTRL 2 to position '+str(track_2[i])
        print ' '
        # go to next position
        caput(CTRL_1_POS, track_1[i], wait=False)
        caput(CTRL_2_POS, track_2[i], wait=True)
        caput(CTRL_1_POS, track_1[i], wait=True) # dummy cmd to check completion
        # wait user input
        raw_input('====> | Press <ENTER> to continue | ')
        print ' '
        # get position readbacks
        ctrl_1_rb = caget(CTRL_1_RB, as_string=True, timeout=10)
        ctrl_2_rb = caget(CTRL_2_RB, as_string=True, timeout=10)
        with open(LOG_FILE_1, 'a') as f1:
            f1.write(ctrl_1_rb+"\n")
        with open(LOG_FILE_2, 'a') as f2:
            f2.write(ctrl_2_rb+"\n")
    # backward motion
    for i in range(point_cnt-1, -1, -1):
        # print msg
        print '--> Move count '+str(2*point_cnt-i)+' / '+str(point_cnt*2)
        print '---> Array position is '+str(i)
        print '---> Moving CTRL 1 to position '+str(track_1[i])
        print '---> Moving CTRL 2 to position '+str(track_2[i])
        print ' '
        # go to previous position
        caput(CTRL_1_POS, track_1[i], wait=False)
        caput(CTRL_2_POS, track_2[i], wait=True)
        caput(CTRL_1_POS, track_1[i], wait=True) # dummy cmd to check completion
        # wait user input
        raw_input('====> | Press <ENTER> to continue | ')
        print ' '
        # get position readbacks
        ctrl_1_rb = caget(CTRL_1_RB, as_string=True, timeout=10)
        ctrl_2_rb = caget(CTRL_2_RB, as_string=True, timeout=10)
        with open(LOG_FILE_1, 'a') as f1:
            f1.write(ctrl_1_rb+"\n")
        with open(LOG_FILE_2, 'a') as f2:
            f2.write(ctrl_2_rb+"\n")
else:
    # forward motion
    for i in range(0, point_cnt):
        # print msg
        print '--> Move count '+str(i+1)+' / '+str(point_cnt)
        print '---> Array position is '+str(i)
        print '---> Moving CTRL 1 to position '+str(track_1[i])
        print '---> Moving CTRL 2 to position '+str(track_2[i])
        print ' '
        # go to next position
        caput(CTRL_1_POS, track_1[i], wait=False)
        caput(CTRL_2_POS, track_2[i], wait=True)
        caput(CTRL_1_POS, track_1[i], wait=True) # dummy cmd to check completion
        # wait user input
        raw_input('====> | Press <ENTER> to continue | ')
        print ' '
        # get position readbacks
        ctrl_1_rb = caget(CTRL_1_RB, as_string=True, timeout=10)
        ctrl_2_rb = caget(CTRL_2_RB, as_string=True, timeout=10)
        with open(LOG_FILE_1, 'a') as f1:
            f1.write(ctrl_1_rb+"\n")
        with open(LOG_FILE_2, 'a') as f2:
            f2.write(ctrl_2_rb+"\n")

print '****************************'
print '*     Program Finished     *'
print '****************************'
print ' '

