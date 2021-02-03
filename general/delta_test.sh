#!/usr/bin/env bash

# DELTA TEST SCRIPT

./move_and_repeat.py \
--points-file "delta_test.txt" \
--repeat-count 10 \
--repeat-reverse-at-end false \
--cmd-pv und:EnMove-Cmd \
--sp-pv und:AxisAMovePos-SP \
--check-after-motion "@und:AxisAActualPosition-Mon == @und:AxisAMovePos-SP +- 0.1" \
--before-motion-timeout 10.0 \
--during-motion-timeout 10.0 \
--after-motion-timeout 10.0 \
--emergency-action-pv und:Stop-Cmd \
--emergency-action-value True \
--command-delay 0.5 \
--log-filename test_log

