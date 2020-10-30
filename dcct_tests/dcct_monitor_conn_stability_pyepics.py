#!/usr/bin/env python

import epics
import datetime
import time

print("\n\n"
" ########## Acquisition Pause Test - DCCT IOC  ##########"
"\n\n")

deltat = float(input("Please enter max allowed interval: "))
print('\n')
prefix = input("Please enter PV prefix: ")
print(prefix)
print('\n')
print("Preparing...\n")

# time delta variable
time_delta = datetime.timedelta(milliseconds=deltat*1000)
# DCCT update flag
dcct_curr_update = 0
# DCCT timestamp flag
dcct_time_update = 0

# current camonitor callback function
def onCurrentChange(pvname=None, value=None, char_value=None,**kw):
    ''' Callback function to monitor PV value change '''
    global dcct_curr_update
    dcct_curr_update += 1

# timestamp camonitor callback function
def onTimestampChange(pvname=None, value=None, char_value=None,**kw):
    ''' Callback function to monitor PV value change '''
    global dcct_time_update
    dcct_time_update += 1

# monitor DCCT current PV
current_mon_pv = epics.PV(prefix+'Current-Mon')
current_mon_pv.add_callback(onCurrentChange)

# monitor DCCT timestamp PV
timestamp_mon_pv = epics.PV(prefix+'Timestamp-Mon')
timestamp_mon_pv.add_callback(onTimestampChange)

# initialize auxiliary variables
dcct_curr_update_old = 0
dcct_time_update_old = 0
time1 = datetime.datetime.now()

print("Start\n")

# main loop
while True:
    # sleep
    time.sleep(deltat/10)
    # verify updates
    time2 = datetime.datetime.now()
    if ((dcct_curr_update == dcct_curr_update_old) and (time2-time1 > time_delta)):
        print('Current meas value got stuck for '+str(time2 - time1))
        print('At '+str(time2)+'\tCurrent= '+current_mon_pv.get(as_string=True, use_monitor=False)+'\n')
    elif (dcct_curr_update != dcct_curr_update_old):
        time1 = datetime.datetime.now()
        dcct_curr_update_old = dcct_curr_update
        #print('meas cnt= '+str(dcct_curr_update)+'\t'+str(datetime.datetime.now()))

