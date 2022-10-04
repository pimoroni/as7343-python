from as7343 import AS7343

as7343 = AS7343()

as7343.set_gain(64)
as7343.set_integration_time(17.857)
as7343.set_measurement_mode(2)
as7343.set_illumination_led(1)

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

