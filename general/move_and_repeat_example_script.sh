#!/usr/bin/env bash

# EXAMPLE MOTION TEST SCRIPT

./move_and_repeat.py \
--points-file "move_and_repeat_example_ioc.txt" \
--repeat-count 3 \
--repeat-reverse-at-end false \
--cmd-pv cmdButton \
--sp-pv target \
--check-during-motion "!@step == 3" \
--check-after-motion "@encoder == @target +- 2" \
--before-motion-timeout 4.0 \
--during-motion-timeout 4.0 \
--after-motion-timeout 20.0 \
--repeat-reverse-at-end true \
--emergency-action-pv cmdButton \
--emergency-action-value off \
--log-filename test_log
