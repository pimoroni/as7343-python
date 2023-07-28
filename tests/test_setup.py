# noqa D100

def test_fw_info(smbus):
    """Test against fake device information stored in hardware mock."""
    from as7343 import AS7343, PART_ID
    as7343 = AS7343()

    auxid, revid, id = as7343.get_version()

    assert auxid == 0x08
    assert revid == 0x07
    assert id == PART_ID
