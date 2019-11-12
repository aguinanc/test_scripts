#!/usr/bin/env python

import visa
import time, datetime
import sys, os
import re, string, struct
import numpy as np
import pandas as pd
import scipy, peakutils

#### SCRIPT SETTINGS ####

# oscilloscope channel
channel_ict1 = 3
channel_ict2 = 4

# ICT sensor sensitivity
DIV_FACTOR = 5

#########################

#### ENUM VALUES ########

# Waveform settings from preamble:

wav_form_dict = {
  0 : "ASCii",
  1 : "BYTE",
  2 : "WORD",
  3 : "LONG",
  4 : "LONGLONG",
  }
acq_type_dict = {
  1 : "RAW",
  2 : "AVERage",
  3 : "VHIStogram",
  4 : "HHIStogram",
  6 : "INTerpolate",
  10 : "PDETect",
  }
acq_mode_dict = {
  0 : "RTIMe",
  1 : "ETIMe",
  3 : "PDETect",
  }
coupling_dict = {
  0 : "AC",
  1 : "DC",
  2 : "DCFIFTY", 
  3 : "LFREJECT",
  }
units_dict = {
  0 : "UNKNOWN",
  1 : "VOLT",
  2 : "SECOND",
  3 : "CONSTANT",
  4 : "AMP",
  5 : "DECIBEL",
  }

#########################

# connection
if 'rm' in globals():
    pass
else:
    global rm
    rm = visa.ResourceManager('@py')

# oscilloscope IP
ip = "10.128.150.78"

# open connection
osc_socket = rm.open_resource('TCPIP::'+ip+'::inst0::INSTR')
print 'Connected'

# set timeout
osc_socket.timeout = 10000

# config waveform to binary 16-bit format
osc_socket.write(':WAVeform:FORMat WORD')
# big-endian
osc_socket.write(':WAVeform:BYTeorder MSBFirst')

# create regex pattern object
non_decimal = re.compile(r'[^\d]+')

# poll osc
while True:
  # give time between queries
  time.sleep(0.1)
  # poll new acquisition flag
  if int(non_decimal.sub('', osc_socket.query(':ADER?'))) == 1:
    #### get data
    # choose osc channel ic1
    osc_socket.write(':WAVeform:SOURce CHANnel'+str(channel_ict1))
    dummy = osc_socket.query('*OPC?')
    # read osc wvf preamble
    preamble_string = osc_socket.query(":WAVeform:PREamble?")
    # split preamble
    (wav_form_ict1, acq_type_ict1, wfmpts_ict1, avgcnt_ict1, x_increment_ict1,
     x_origin_ict1, x_reference_ict1, y_increment_ict1, y_origin_ict1,
     y_reference_ict1, coupling_ict1, x_display_range_ict1,
     x_display_origin_ict1, y_display_range_ict1, y_display_origin_ict1,
     date_ict1, time_ict1, frame_model_ict1, acq_mode_ict1, completion_ict1,
     x_units_ict1, y_units_ict1, max_bw_limit_ict1, min_bw_limit_ict1
    ) = string.split(preamble_string, ",")
    # read osc waveform
    data_ict1 = osc_socket.query_binary_values(
    ':WAVeform:DATA?', datatype='H', is_big_endian=True)
    dummy = osc_socket.query('*OPC?')
    # choose osc channel ict2
    osc_socket.write(':WAVeform:SOURce CHANnel'+str(channel_ict2))
    dummy = osc_socket.query('*OPC?')
    # read osc wvf preamble
    preamble_string = osc_socket.query(":WAVeform:PREamble?")
    # split preamble
    (wav_form_ict2, acq_type_ict2, wfmpts_ict2, avgcnt_ict2, x_increment_ict2,
     x_origin_ict2, x_reference_ict2, y_increment_ict2, y_origin_ict2,
     y_reference_ict2, coupling_ict2, x_display_range_ict2,
     x_display_origin_ict2, y_display_range_ict2, y_display_origin_ict2,
     date_ict2, time_ict2, frame_model_ict2, acq_mode_ict2, completion_ict2,
     x_units_ict2, y_units_ict2, max_bw_limit_ict2, min_bw_limit_ict2
    ) = string.split(preamble_string, ",")
    # read osc waveform
    data_ict2 = osc_socket.query_binary_values(
    ':WAVeform:DATA?', datatype='h', is_big_endian=True)
    dummy = osc_socket.query('*OPC?')
    #### process data
    # convert data to numpy arrays
    data_ict1 = np.asarray(data_ict1)
    data_ict2 = np.asarray(data_ict2)
    # convert data from counts to engineering units
    data_ict1 = data_ict1 * y_increment_ict1 + y_origin_ict1
    data_ict2 = data_ict2 * y_increment_ict2 + y_origin_ict2
    # subtract base line from data
    data_ict1 = base_line_sub(data_ict1)
    data_ict2 = base_line_sub(data_ict2)
    # integrate wvfs using trapezoidal rule
    ict1_charge = np.trapz(data_ict1)
    ict2_charge = np.trapz(data_ict2)
    # divide by sensor conv factor
    ict1_charge = ict1_charge / DIV_FACTOR
    ict2_charge = ict2_charge / DIV_FACTOR

osc_socket.close()
