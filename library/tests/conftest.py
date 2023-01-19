import sys
import mock
import pytest
import struct
from i2cdevice import MockSMBus
from .tools import CALIBRATED_VALUES


class SMBusFakeDevice(MockSMBus):
    def __init__(self, i2c_bus):
        MockSMBus.__init__(self, i2c_bus)

        self.regs = [0b10000001 for _ in range(255)]

        # Virtual registers, thes contain the data actually used
        self.regs[0x00] = 0x88  # Fake HW type
        self.regs[0x01] = 0x77  # Fake HW version
        self.regs[0x02] = 0xFE  # Fake FW version MSB (Sub, Minor)
        self.regs[0x03] = 0xFF  # Fake FW version LSB (Minor, Major)
        self.regs[0x04] = 0x02  # Control Register

        self.regs[0x5A] = 0b10000001

        # Prime the Calibrated Data registers with fake data
        self.regs[0x14:24] = [ord(c) if type(c) is str else c for c in struct.pack(
            '>ffffff',
            *reversed(CALIBRATED_VALUES)
        )]


@pytest.fixture(scope='function', autouse=False)
def smbus():
    """Mock smbus module."""
    smbus = mock.MagicMock()
    smbus.SMBus = SMBusFakeDevice
    sys.modules['smbus'] = smbus
    yield smbus
    del sys.modules['smbus']