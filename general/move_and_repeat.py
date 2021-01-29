#!/usr/bin/env python

########################### Run in python 3 ###########################

import sys
import re
import numpy as np
import argparse
import time
import datetime
import traceback
import math

from epics import caget, caput

#### Parsing

# setup
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    '--points-file',
    action="store", dest="points_file", type=str,
    help="Name of file with points to move to.",
    required=True,
)
parser.add_argument(
    '--repeat-count',
    action="store", dest="repeat_count", type=int, default=0,
    help="How many times to repeat points. Can be Inf.",
    required=False,
)
parser.add_argument(
    '--repeat-reverse-at-end',
    action="store", dest="repeat_reverse_at_end", type=str, default="False",
    help="When repeating points from file, whether to start\n"
         "from beginning (False) or reverse read order (True).",
    required=False,
)
parser.add_argument(
    '--cmd-pv',
    action="append", dest="cmd_pv_list", type=str,
    help="Append to list of PVs that start motion.",
    required=False,
)
parser.add_argument(
    '--sp-pv',
    action="append", dest="sp_pv_list", type=str,
    help="Append to list of PVs for position set point.",
    required=True,
)
parser.add_argument(
    '--mon-pv',
    action="append", dest="mon_pv_list", type=str,
    help="Append to list of PVs to monitor during motion.",
    required=False,
)
parser.add_argument(
    '--check-after-motion',
    action="append", dest="check_after_motion_list",type=str,
    help="List of conditions to check after a motion completes.\n"
         "Examples:\n"
         "          <pv name> == <pv name>\n"
         "          <pv name> == <value>\n"
         "          <pv name> == <pv name>+-<tolerance>\n"
         "          <pv name> == <value>+-<tolerance>\n"
         "          wait\n"
         "Supported operators: '==', '>', '<'\n"
         "The 'wait' keyword forces the check to proceed only after"
         " timeout.\n"
         "An exclamation mark '!' before the condition configures the\n"
         " test to fail if the corresponding condition is met.\n",
    required=False,
)
parser.add_argument(
    '--after-motion-timeout',
    action="store", dest="after_motion_timeout", type=float, default=10.0,
    help="The time, in seconds, available for after-motion\n"
         "conditions to be met until timeout happens.",
    required=False,
)
parser.add_argument(
    '--check-during-motion',
    action="append", dest="check_during_motion_list", type=str,
    help="List of conditions to check during motion.\n"
         "Examples:\n"
         "          <pv name> == <pv name>\n"
         "          <pv name> == <value>\n"
         "          <pv name> == <pv name>+-<tolerance>\n"
         "          <pv name> == <value>+-<tolerance>\n"
         "          wait\n"
         "Supported operators: '==', '>', '<'\n"
         "The 'wait' keyword forces the check to proceed only after"
         " timeout.\n"
         "An exclamation mark '!' before the condition configures the\n"
         " test to fail if the corresponding condition is met.\n",
    required=False,
)
parser.add_argument(
    '--during-motion-timeout',
    action="store", dest="during_motion_timeout", type=float, default=1.0,
    help="The time available for during-motion conditions\n"
         "to be met until timeout.",
    required=False,
)
parser.add_argument(
    '--check-before-motion',
    action="append", dest="check_before_motion_list", type=str,
    help="List of conditions to check before a motion starts.\n"
         "Examples:\n"
         "          @<pv name> == @<pv name>\n"
         "          @<pv name> == <value>\n"
         "          @<pv name> == @<pv name>+-<tolerance>\n"
         "          @<pv name> == <value>+-<tolerance>\n"
         "          wait\n"
         "Supported operators: '==', '>', '<'\n"
         "The 'wait' keyword forces the check to proceed only after"
         " timeout.\n"
         "An exclamation mark '!' before the condition configures the\n"
         " test to fail if the corresponding condition is met.\n",
    required=False,
)
parser.add_argument(
    '--before-motion-timeout',
    action="store", dest="before_motion_timeout", type=float, default=1.0,
    help="The time available for before-motion conditions\n"
         "to be met until timeout.",
    required=False,
)
parser.add_argument(
    '--emergency-action-pv',
    action="store", dest="emergency_action_pv_list", type=str,
    help="Append to the list of PVs that should be set when an\n"
         " emergency condition (with '!') is met in some check.",
    required=False,
)
parser.add_argument(
    '--emergency-action-value',
    action="store", dest="emergency_action_value_list", type=str,
    help="Append to the list of values to be passed to the emergency\n"
         " action PVs when an emergency condition (with '!') is met\n"
         "for some check.",
    required=False,
)

# parse
args = parser.parse_args()

points_file = args.points_file
repeat_count = args.repeat_count

reverse_at_end = args.repeat_reverse_at_end.lower()
if reverse_at_end == 'true' or reverse_at_end == '1':
    reverse_at_end = True
elif reverse_at_end == 'false' or reverse_at_end == '0':
    reverse_at_end = False
else:
    raise TypeError('reverse_at_end argument must be boolean')

# assign variables
cmd_pv_list = args.cmd_pv_list
sp_pv_list = args.sp_pv_list
mon_pv_list = args.mon_pv_list
check_after_motion_list = args.check_after_motion_list
check_during_motion_list = args.check_during_motion_list
check_before_motion_list = args.check_before_motion_list
after_motion_timeout = args.after_motion_timeout
during_motion_timeout = args.during_motion_timeout
before_motion_timeout = args.before_motion_timeout
emergency_action_pv_list = args.emergency_action_pv_list
emergency_action_value_list = args.emergency_action_value_list

# replace None values for lists
if cmd_pv_list is None:
    cmd_pv_list = []
if sp_pv_list is None:
    sp_pv_list = []
if mon_pv_list is None:
    mon_pv_list = []
if check_after_motion_list is None:
    check_after_motion_list = []
if check_during_motion_list is None:
    check_during_motion_list = []
if check_before_motion_list is None:
    check_before_motion_list = []
if emergency_action_pv_list is None:
    emergency_action_pv_list = []
if emergency_action_value_list is None:
    emergency_action_value_list = []

# Global variables
list_of_positions = []
num_columns = -1
iter_count = 0

# try to open input file
try:
    with open(points_file, 'r') as f:
        for line in f:
            # remove white spaces from line
            clean_line = line.replace(' ','').replace('\r','')
            clean_line = clean_line.replace('\n','')
            # ignore empty lines or comments
            if len(clean_line) == 0:
                continue
            if clean_line[0] == '#':
                continue
            # split line by comma, semicolon or tab characters
            point = re.split('[,;\t]', clean_line)
            # parse coordinates to float
            point = [float(coord) for coord in point]
            # first row defines number of columns
            if num_columns == -1:
                num_columns = len(point)
            # always check number of columns
            elif num_columns != len(point):
                print("Error - input file rows with different number"
                      " of columns")
                sys.exit(1)
            # insert point into list of points
            list_of_positions.append(point)
except Exception:
    traceback.print_exc(file=sys.stdout)
    print('Error - could not open file '+str(points_file))
    sys.exit(1)

# check number of points
if len(list_of_positions) < 1:
    print("Input file has zero points. Nothing to be done.")
    sys.exit(0)

# verify if there are enough SP PVs to control positions
if len(sp_pv_list) != num_columns:
    # not enough PVs to control all coordinates
    print("Error - number of set point PVs is smaller than number of"
          " columns in input file")
    sys.exit(1)

# check repeat count
if repeat_count < 0:
    repeat_count = 0

# check match between number of emergency action PVs and values
if len(emergency_action_pv_list) != len(emergency_action_value_list):
    print("Error - number of emergency action PVs and values passed"
          " does not match.")
    sys.exit(1)

#### Auxiliary Functions

def emergency_stop(emergency_action_pv_list,
                   emergency_action_value_list):
    """ Command all PVs necessary to perform a motion Stop """
    try:
        list_size = len(emergency_action_pv_list)
        for i in range(0, list_size):
            caput(emergency_action_pv_list[i],
                  emergency_action_value_list)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        print('Error - failed to send motion stop commands')

def check_conditions(condition_list, timeout):
    """ Check if condition about PVs are met until timeout 

    Return value: (check_result, (value1, value2), last_condition_idx,
                   timeout_true, is_emergency) """
    t_start = time.time()
    timed_out = False
    cond_count = len(condition_list)
    wait = False
    t_delay = 0.1
    res = (False, None)
    emergency_cond_idx_list = []
    # if empty list, return immediately
    if cond_count == 0:
        return (True, None, -1, False, False)
    # check if must wait until timeout
    for condition in condition_list:
        if condition.replace(' ','') == 'wait':
            wait = True
    # check which conditions are of the emergency type
    for idx in range(0, cond_count):
        if '!' in condition_list[idx]:
            emergency_cond_idx_list.append(idx)
    # monitor conditions until they are true
    while True:
        if time.time() - t_start > timeout:
            timed_out = True
            break
        all_ok = True
        for i in range(0, cond_count):
            condition = condition_list[i]
            res = check_condition(condition)
            # regular condition not met yet
            if res[0] is False:
                all_ok = False
            # met condition is an emergency, test should stop
            if res[0] is True and i in emergency_cond_idx_list:
                return (res[0], res[1], i, False, True)
        if all_ok:
            break
        time.sleep(t_delay)
    if wait and not timed_out:
        while time.time() - t_start < timeout:
            time.sleep(t_delay)
        return (res[0], res[1], cond_count-1, False, False)
    return (res[0], res[1], cond_count-1, timed_out, False)

def check_condition(cond):
    """ Check if condition about PVs are met until timeout 

    Return value: (check_result, (value1, value2)) """
    try:
        clean_cond = cond.replace(' ','').replace('!','')
        comp = ''
        operand = []
        if '==' in clean_cond:
            operand = clean_cond.split('==')
            comp = 'eq'
        elif '>' in clean_cond:
            operand = clean_cond.split('>')
            comp = 'gt'
        elif '<' in clean_cond:
            operand = clean_cond.split('<')
            comp = 'lt'
        if comp == '' or len(operand) != 2:
            return (False, None)
        value1 = ''
        value2 = ''
        value2_max = 0.0
        value2_min = 0.0
        tol = 0.0
        if '+-' in operand[1]:
            aux = operand[1].split('+-')
            operand[1] = aux[0]
            tol = float(aux[1])
        if '@' not in operand[0]:
            value1 = operand[0]
        else:
            operand[0] = operand[0].replace('@','')
            value1 = caget(operand[0], as_string=True, timeout=0.5)
        if '@' not in operand[1]:
            value2 = operand[1]
        else:
            operand[1] = operand[1].replace('@','')
            value2 = caget(operand[1], as_string=True, timeout=0.5)
        # define tolerance boundaries
        if tol != 0:
            value2_max = float(value2) + abs(tol)
            value2_min = float(value2) - abs(tol)
        else:
            value2_max = value2
            value2_min = value2
        # apply comparators
        check = False
        if comp == 'eq':
            if tol != 0.0:
                check = (value1 <= value2_max) and (value1 >= value2_min)
            else:
                check = (value1 == value2)
        elif comp == 'gt':
            if tol != 0.0:
                check = value1 > value2_min
            else:
                check = float(value1) > float(value2)
        elif comp == 'lt':
            if tol != 0.0:
                check = value1 < value2_max
            else:
                check = float(value1) < float(value2)
        return (check, (value1, value2))
    except Exception:
        traceback.print_exc(file=sys.stdout)

    return (False, None)

#### Movement Procedure

print('\n'
      '***********************************\n'
      '*  EPICS Device Positioning Test  *\n'
      '***********************************\n\n'
)

# show summary to user

# < still to be written > 

# wait user input
input('===> | Press <ENTER> to start test |\n\n')

try:
    # motion should start reading points forward
    scan_start = 0
    scan_end = len(list_of_positions)
    step = 1
    while iter_count < repeat_count:
        iter_count = iter_count + 1
        # move to each position listed, for each axis
        for idx in range(scan_start, scan_end, step):
            # store point
            point = list_of_positions[idx]
            # print info to user
            print('\n\n')
            print('* New point at {0}.'.format(point))
            print('  {0}/{1} points.'.format(idx+1,
                abs(scan_end - scan_start)))
            print('  {0}/{1} repetitions.\n'.format(iter_count,
                repeat_count))
            # check conditions BEFORE MOVE
            sys.stdout.write('    Checking conditions before move...')
            res = check_conditions(check_before_motion_list,
                                   before_motion_timeout)
            status_check = res[0]
            values = res[1]
            cond_idx = res[2]
            status_timeout = res[3]
            is_emergency = res[4]
            if is_emergency:
                print('Error - emergency condition '
                      +str(check_before_motion_list[cond_idx])
                      +' was triggered.')
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            elif values is None and status_check is False:
                print('Error - could not process condition BEFORE move: '
                      +str(check_before_motion_list[cond_idx])+'.')
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            elif status_timeout is True:
                print('Error - timeout while processing conditions BEFORE'
                      ' move. Profile repetition #'+str(iter_count)+
                      ', point #'+str(idx)+'. Last condition being '
                      'checked: '+str(check_before_motion_list[cond_idx])
                      +'for value1='+str(values[0])+'and value2='
                      +str(values[1]))
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            else:
                # write to the same line
                sys.stdout.write('  OK\n')
            # MAKE MOVE
            print('    Starting motion.')
            # update set points
            for coord in range(0, len(point)):
                caput(sp_pv_list[coord], point[coord], wait=False)
            # set command PVs
            for cmd_pv in cmd_pv_list:
                caput(cmd_pv, 1, wait=False)
            # check conditions DURING MOVE
            sys.stdout.write('    Checking conditions during move...')
            res = check_conditions(check_during_motion_list,
                                   during_motion_timeout)
            status_check = res[0]
            values = res[1]
            cond_idx = res[2]
            status_timeout = res[3]
            is_emergency = res[4]
            if is_emergency:
                print('Error - emergency condition '
                      +str(check_during_motion_list[cond_idx])
                      +' was triggered.')
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            elif values is None and status_check is False:
                print('Error - could not process condition DURING move: '
                      +str(check_during_motion_list[cond_idx])+'.')
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            elif status_timeout is True:
                print('Error - timeout while processing conditions DURING'
                      ' move. Profile repetition #'+str(iter_count)+
                      ', point #'+str(idx)+'. Last condition being '
                      'checked: '+str(check_during_motion_list[cond_idx])
                      +'for value1='+str(values[0])+'and value2='
                      +str(values[1]))
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            else:
                # write to the same line
                sys.stdout.write('  OK\n')
            # check conditions AFTER MOVE
            sys.stdout.write('    Checking conditions after move...')
            res = check_conditions(check_after_motion_list,
                                   after_motion_timeout)
            status_check = res[0]
            values = res[1]
            cond_idx = res[2]
            status_timeout = res[3]
            is_emergency = res[4]
            if is_emergency:
                print('Error - emergency condition '
                      +str(check_after_motion_list[cond_idx])
                      +' was triggered.')
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            elif values is None and status_check is False:
                print('Error - could not process condition AFTER move: '
                      +str(check_after_motion_list[cond_idx])+'.')
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            elif status_timeout is True:
                print('Error - timeout while processing conditions AFTER'
                      ' move. Profile repetition #'+str(iter_count)+
                      ', point #'+str(idx)+'. Last condition being '
                      'checked: '+str(check_after_motion_list[cond_idx])
                      +'for value1='+str(values[0])+'and value2='
                      +str(values[1]))
                emergency_stop(emergency_action_pv_list,
                               emergency_action_value_list)
                sys.exit(1)
            else:
                # write to the same line
                sys.stdout.write('  OK\n')
        # if configured to, reverse position scan
        if reverse_at_end:
            if scan_start == 0:
                scan_start = scan_end - 1
                scan_end = -1
                step = -1
            else:
                scan_end = scan_start + 1
                scan_start = 0
                step = 1
except Exception:
    traceback.print_exc(file=sys.stdout)
    print('Error - unexpected failure')
    sys.exit(1)


print('\n'
      '*****************************'
      '*       Test Finished       *'
      '*****************************'
      '\n '
)

