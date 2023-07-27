# noqa D100

def test_fw_info(smbus):
    """Test against fake device information stored in hardware mock."""
    from as7343 import AS7343
    as7343 = AS7343()

    hw_type, hw_version, fw_version = as7343.get_version()

    assert hw_version == 0x77
    assert hw_type == 0x88
    assert fw_version == '15.63.62'
