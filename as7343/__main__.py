"""Library for the AS7343 Visible Light Spectral Sensor."""
import as7343

if __name__ == '__main__':
    as7343.soft_reset()

    hw_type, hw_version, fw_version = as7343.get_version()

    print('{}'.format(fw_version))

    as7343.set_gain(64)

    as7343.set_integration_time(17.857)

    as7343.set_measurement_mode(2)

    # as7343.set_illumination_led_current(12.5)
    as7343.set_illumination_led(1)
    # as7343.set_indicator_led_current(2)
    # as7343.set_indicator_led(1)

    try:
        while True:
            values = as7343.get_calibrated_values()
            print("""
Red:    {}
Orange: {}
Yellow: {}
Green:  {}
Blue:   {}
Violet: {}""".format(*values))
    except KeyboardInterrupt:
        as7343.set_measurement_mode(3)
        as7343.set_illumination_led(0)
