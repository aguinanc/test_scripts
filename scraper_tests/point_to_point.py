import time
import numpy as np
from epics import caput, caget
import optparse

NUM_MOVES = 30
DELAY_BETWEEN_MOVES = 10 # seg
POS_PV = 'vac-test:galil:AbsPos-SP'
MON_PV = 'vac-test:galil:EncPos-Mon'
START_POS = 10.265
END_POS = 19.5

STEP = 0.8

TOL = 0.1 # mm

OUT_FILE = 'scrap_test_readings.txt'
ERR_FILE = 'scrap_error_output.txt'

# Parsing
## setup
parser = optparse.OptionParser()
parser.add_option(
        '--start',
        action="store",
        dest="start",
        type="float",
        default=START_POS,
        help="CTRL start position")
parser.add_option(
        '--end',
        action="store",
        dest="end",
        type="float",
        default=END_POS,
        help="CTRL end position")
parser.add_option(
        '--step',
        action="store",
        dest="step",
        type="float",
        default=STEP,
        help="CTRL step size")
parser.add_option(
        '--maxmoves',
        action="store",
        dest="maxmoves",
        type="int",
        default=NUM_MOVES,
        help="CTRL maximum steps in the same direction")
parser.add_option(
        '--outfile',
        action="store",
        dest="outfile",
        type="string",
        default=OUT_FILE,
        help="Output file name")
# parse
(options, args) = parser.parse_args()

#if options.end > options.start:
#    pos_list = np.arange(options.start, options.end, np.abs(options.step))
#    pos_list = np.array(pos_list[:options.maxmoves])
#    pos_list_return = np.flip(pos_list)
#    pos_list = np.concatenate((pos_list[:-1], pos_list_return))
#if options.end < options.start:
#    pos_list = np.arange(options.start, options.end, np.abs(options.step))
#    pos_list = np.array(pos_list[:options.maxmoves])
#    pos_list_return = np.flip(pos_list)
#    pos_list = np.concatenate((pos_list[:-1], pos_list_return))
#else:
#    pos_list = []

if options.end > options.start:
    pos_list = np.arange(options.start, options.end+np.abs(options.step), np.abs(options.step))
    pos_list = np.array(pos_list[:options.maxmoves])
    pos_list_return = np.flip(pos_list)
    pos_list = np.concatenate((pos_list[:-1], pos_list_return))
else:
    pos_list = [options.start - i*options.step for i in range(0, options.maxmoves)]
    pos_list = np.array(pos_list[:options.maxmoves])
    pos_list = [p for p in pos_list if p >= options.end]
    pos_list_return = np.flip(pos_list)
    pos_list = np.concatenate((pos_list[:-1], pos_list_return))

outfile = options.outfile

i = 0
for pos in pos_list:
    dummy_input = input('Press <ENTER> to proceed')
    rbv = caget(MON_PV)
    with open(outfile, 'a') as f:
        f.write('{}: Cmd position= {}, Encoder reading= {}'.format(time.ctime(), pos, rbv))
        f.write('\n')
    i += 1
    print('# Move {} '.format(i))
    caput(POS_PV, pos)
    #time.sleep(DELAY_BETWEEN_MOVES)
    rbv = caget(MON_PV)
    if np.abs(rbv - pos) > TOL:
        with open(ERR_FILE, 'a') as f:
            f.write('{}: Error moving to {}, got only to {}'.format(time.ctime(), pos, rbv))
            f.write('\n')

print('Waiting to save last position ...')
time.sleep(DELAY_BETWEEN_MOVES)
with open(outfile, 'a') as f:
    rbv = caget(MON_PV)
    f.write('{}: Final position, Encoder reading= {}'.format(time.ctime(), rbv))
    f.write('\n')
print('Done')

