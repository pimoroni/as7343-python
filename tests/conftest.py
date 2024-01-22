import sys

import mock
import pytest
from i2cdevice import MockSMBus


class SMBusFakeDevice(MockSMBus):
    def __init__(self, i2c_bus):
        MockSMBus.__init__(self, i2c_bus, default_registers={
            0x58: 0x08,       # Fake aux ID
            0x59: 0x07,       # Fake rev ID
            0x5A: 0b10000001  # Fake ID (part number?)
        })

    def write_i2c_block_data(self, i2c_address, register, values):
        self.regs[register:register + len(values)] = values

    def read_i2c_block_data(self, i2c_address, register, length):
        # Catch reads from FDATA and decriment FIFO_LVL
        if register == 0xFE and self.regs[0xFD] > 0:
            self.regs[0xFD] -= 1

        return self.regs[register:register + length]


@pytest.fixture(scope='function', autouse=False)
def smbus():
    """Mock smbus module."""
    smbus = mock.MagicMock()
    smbus.SMBus = SMBusFakeDevice
    sys.modules['smbus2'] = smbus
    yield smbus
    del sys.modules['smbus2']