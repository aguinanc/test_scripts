# Scraper tests

### Overall

The scripts in this folder were used in the process of testing and calibration of the Sirius Vertical and Horizontal Scrapers.

### Calibration

The Scraper calibration consisted of building a table describing the relationship between in-air linear stage and in-vacuum device tip positions, which was provided to the IOC for coordinate conversion of command and readback values.

#### Scripts

- `scraper_measure.py`: moves two motors, each for a specified distance, provided a given number of stop points. The position readback value for each point is saved to a file. This script requires the PyEPICS library and a [DMC30017 EPICS IOC](https://github.com/lnls-dig/galil-dmc30017-epics-ioc) running for each controller.
