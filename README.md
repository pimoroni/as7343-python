# AS7343 Spectral Sensor

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/as7343-python/test.yml?branch=main)](https://github.com/pimoroni/as7343-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/as7343-python/badge.svg?branch=main)](https://coveralls.io/github/pimoroni/as7343-python?branch=main)
[![PyPi Package](https://img.shields.io/pypi/v/pimoroni-as7343.svg)](https://pypi.python.org/pypi/pimoroni-as7343)
[![Python Versions](https://img.shields.io/pypi/pyversions/pimoroni-as7343.svg)](https://pypi.python.org/pypi/pimoroni-as7343)

AS7343 is a 14-channel multi-purpose spectral sensor. It can detect 14 spectral channels - 12 in the visible spectrum (VIS) to near-infrared (NIR) range, a clear channel and flicker channel.

You can buy our AS7343 breakout [here](https://shop.pimoroni.com/products/as7343-14-channel-multi-spectral-sensor-breakout)!

## Installing

### Full install (recommended):

We've created an easy installation script that will install all pre-requisites and get your AS7343
up and running with minimal efforts. To run it, fire up Terminal which you'll find in Menu -> Accessories -> Terminal
on your Raspberry Pi desktop, as illustrated below:

![Finding the terminal](http://get.pimoroni.com/resources/github-repo-terminal.png)

In the new terminal window type the command exactly as it appears below (check for typos) and follow the on-screen instructions:

```bash
git clone https://github.com/pimoroni/as7343-python
cd as7343-python
./install.sh
```

**Note** Libraries will be installed in the "pimoroni" virtual environment, you will need to activate it to run examples:

```
source ~/.virtualenvs/pimoroni/bin/activate
```

### Development:

If you want to contribute, or like living on the edge of your seat by having the latest code, you can install the development version like so:

```bash
git clone https://github.com/pimoroni/as7343-python
cd as7343-python
./install.sh --unstable
```

The install script should do it for you, but in some cases you might have to enable the i2c bus.

On a Raspberry Pi you can do that like so:

```
sudo raspi-config nonint do_i2c 0
```

