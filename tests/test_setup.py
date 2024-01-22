# noqa D100
import pytest


def test_fw_info(smbus):
    """Test against fake device information stored in hardware mock."""
    from as7343 import AS7343, PART_ID
    as7343 = AS7343()

    auxid, revid, id = as7343.get_version()

    assert auxid == 0x08
    assert revid == 0x07
    assert id == PART_ID


def test_fw_info_fail(smbus):
    """Test part ID check fails with RuntimeError."""
    from as7343 import AS7343
    i2c_dev = smbus.SMBus(1)
    i2c_dev.regs[0x5A] = 0b11111111  # Wrong part ID

    with pytest.raises(RuntimeError):
        _ = AS7343(i2c_dev=i2c_dev)
