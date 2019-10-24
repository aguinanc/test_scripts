#!/usr/bin/env python

##############################################
#
#             ICT PRECISION TEST
#
# Desc.: Gather data from a ICT without beam
#        to allow measurement precision and 
#        offset estimation.
#
##############################################

from epics import caget, caput, ca
import time
from datetime import datetime
from os import system

##############################################
# MACROS

P_DMM = ""
P_TIM = ""
TOTAL_INTERVAL = 6 * 3600

SAVE_FILE_CHARGE = 'ICT_Precision_Meas_Charge'
SAVE_FILE_TIME = 'ICT_Precision_Meas_Time'

MAX_WINDOW_SIZE = 385
START_DELAY = 111
SAMPLE_DELAY = 1

##############################################
# VARIABLES

# init charge value
old_charge = -1000
curr_charge = old_charge

##############################################
# UTILITY

def get_when_changed(pv_name, previous_val, timeout=0)
  start_time = datetime.utcnow()
  new_val = previous_val
  while new_val == previous_val:
    new_val = caget(pv_name, use_monitor=True)
    curr_time = datetime.utcnow()
    if (timeout != 0) and ((curr_time - start_time) >= timeout):
      break
  return new_val, curr_time


##############################################
# MAIN LOOP

loop_start = datetime.now()
SAVE_FILE_CHARGE=SAVE_FILE_CHARGE+str(loop_start)
SAVE_FILE_TIME=SAVE_FILE_TIME+str(loop_start)
loop_start = datetime.utcnow()
while datetime.utcnow() - loop_start < TOTAL_INTERVAL:
  loop_start = datetime.utcnow()
  # create empty list
  charge_list = []
  time_list = []
  # get charge value for different settings
  for curr_cnt in range(1, MAX_WINDOW_SIZE+1):
    # get charge value after change
    chg, t = get_when_changed(P_DMM+'Charge-Mon', old_charge)
    charge_list.append(chg)
    time_list.append(t)
    # update averaging window size
    caput(P_DMM+'SampleCnt-SP', curr_cnt, SYNC)
    # update averaging window start time
    caput(P_TIM+'Delay-SP'), MAX_WINDOW_SIZE - curr_cnt, SYNC)
  # save results to file
  list_length = len(charge_list)
  for idx in range(0, list_length):
    with open(SAVE_FILE_CHARGE, 'a') as f:
      if idx < list_length - 1:
        f.write(str(charge_list[idx])+', ')
      else:
        f.write(str(charge_list[idx])+'\n')
    with open(SAVE_FILE_TIME, 'a') as f:
      if idx < list_length - 1:
        f.write(str(time_list[idx])+', ')
      else:
        f.write(str(time_list[idx])+'\n')

