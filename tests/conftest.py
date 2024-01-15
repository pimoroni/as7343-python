import sys

import mock
import pytest
from i2cdevice import MockSMBus


class SMBusFakeDevice(MockSMBus):
    def __init__(self, i2c_bus):
        MockSMBus.__init__(self, i2c_bus)

        self.regs = [0 for _ in range(255)]

        # Virtual registers, these contain the data actually used
        self.regs[0x58] = 0x08  # Fake aux ID
        self.regs[0x59] = 0x07  # Fake rev ID
        self.regs[0x5A] = 0b10000001  # Fake ID (part number?)


@pytest.fixture(scope='function', autouse=False)
def smbus():
    """Mock smbus module."""
    smbus = mock.MagicMock()
    smbus.SMBus = SMBusFakeDevice
    sys.modules['smbus2'] = smbus
    yield smbus
    del sys.modules['smbus2']