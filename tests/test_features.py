# noqa D100
import pytest


def test_set_integration_time(smbus):
    """Test the set_integration_time method against various values."""
    from as7343 import AS7343
    as7343 = AS7343()

    # Integration time is stored as 2.78us per lsb
    # so returned values experience quantization
    # int(50000/2.78)*2.78 == 49998.299
    as7343.set_integration_time(50000)
    assert round(as7343._as7343.ASTEP.get_ASTEP(), 1) == 49998.3
    assert as7343._as7343.ATIME.get_ATIME() == 0  # Repeat once

    # For example: 27800 will alias to 27799.99
    # int(27800/2.78)*2.78 = 27799.999
    as7343.set_integration_time(27800)
    assert round(as7343._as7343.ASTEP.get_ASTEP(), 1) == 27800.0
    assert as7343._as7343.ATIME.get_ATIME() == 0  # Repeat once

    # All input values are masked by i2cdevice according
    # to the mask supplied.
    # In the case of Integration Time this is 0xFFFF
    # Values greater than 65535 or 182187.3 require
    # ATIME to be set, repeating the delay.
    # So 200,000 will be two lots of 100,000us which
    # should alias to 99999.379
    as7343.set_integration_time(200000)
    assert round(as7343._as7343.ASTEP.get_ASTEP(), 1) == 99999.4
    assert as7343._as7343.ATIME.get_ATIME() == 1  # Repeat twice


def test_set_gain(smbus):
    """Test the set_gain method against various values."""
    from as7343 import AS7343
    as7343 = AS7343()

    as7343.set_gain(1)
    assert as7343._as7343.CFG1.get_AGAIN() == 1

    as7343.set_gain(0.5)
    assert as7343._as7343.CFG1.get_AGAIN() == 0.5

    as7343.set_gain(1024)
    assert as7343._as7343.CFG1.get_AGAIN() == 1024

    # Should snap to the highest gain value
    as7343.set_gain(9999)
    assert as7343._as7343.CFG1.get_AGAIN() == 2048

    # Should snap to the lowest gain value
    as7343.set_gain(-1)
    assert as7343._as7343.CFG1.get_AGAIN() == 0.5


def test_set_measurement_time(smbus):
    """Test the set_measurement_mode method."""
    from as7343 import AS7343
    as7343 = AS7343()

    # Measurement time is stored as 2.78ms per lsb
    # int(50/2.78) * 2.78 = 47.26
    as7343.set_measurement_time(50)
    assert as7343._as7343.WTIME.get_WTIME() == 47.26


def test_set_illumination_led_current(smbus):
    """Test the set_illumination_led_current method."""
    from as7343 import AS7343
    as7343 = AS7343()

    as7343.set_illumination_led_current(8)
    assert as7343._as7343.LED.get_LED_DRIVE() == 8

    # Since the encoded value is divided by two,
    # it's always aliased to the nearest round number
    as7343.set_illumination_led_current(15)
    assert as7343._as7343.LED.get_LED_DRIVE() == 14

    # Check the 16mA safety current limit
    with pytest.raises(RuntimeError):
        as7343.set_illumination_led_current(17)


def test_illumination_led(smbus):
    """Test the illumination_led method."""
    from as7343 import AS7343
    as7343 = AS7343()

    as7343.set_illumination_led(True)
    assert as7343._as7343.LED.get_LED_ACT() == 1

    as7343.set_illumination_led(False)
    assert as7343._as7343.LED.get_LED_ACT() == 0


def test_soft_reset(smbus):
    """Test the soft_reset method."""
    from as7343 import AS7343
    as7343 = AS7343()

    as7343.soft_reset()
    assert as7343._as7343.CONTROL.get_SW_RESET() == 1
