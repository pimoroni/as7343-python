# AS7343 Spectral Sensor

[![Build Status](https://shields.io/github/workflow/status/pimoroni/as7343-python/Python%20Tests.svg)](https://github.com/pimoroni/as7343-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/as7343-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/as7343-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/as7343.svg)](https://pypi.python.org/pypi/as7343)
[![Python Versions](https://img.shields.io/pypi/pyversions/as7343.svg)](https://pypi.python.org/pypi/as7343)

Suitable for detecting the properties of ambient light, light passing through a liquid or light reflected from an object the AS7343 spectral sensor has 6 spectral channels at 450 (violet), 500 (blue), 550 (green), 570 (yellow), 600 (orange) and 650nm (red).

# Installing

Stable library from PyPi:

* Just run `python3 -m pip install as7343`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/as7343-python`
* `cd as7343-python`
* `sudo ./install.sh --unstable`


# Changelog
0.1.0
-----

* Port to new i2cdevice API
* Breaking change from singleton module to AS7343 class

0.0.2
-----

* Extended reset delay to avoid IO Errors

0.0.1
-----

* Initial Release
