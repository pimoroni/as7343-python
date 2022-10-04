# noqa D100
import sys
import mock  # noqa: E402
from .tools import SMBusFakeAS7343  # noqa: E402


def test_fw_info():
    """Test against fake device information stored in hardware mock."""
    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeAS7343
    sys.modules['smbus'] = smbus
    from as7343 import AS7343

    as7343 = AS7343()

    hw_type, hw_version, fw_version = as7343.get_version()

    assert hw_version == 0x77
    assert hw_type == 0x88
    assert fw_version == '15.63.62'
