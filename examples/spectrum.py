import time
from as7343 import AS7343

as7343 = AS7343()

as7343.set_gain(512)
as7343.set_integration_time(100 * 1000)
as7343.set_channels(18)
as7343.set_illumination_led(True)

try:
    while True:
        values = as7343.get_data()
        if values is None:
            continue
        data = values[0]
        data.update(values[1])
        data.update(values[2])
        print("""
Red:    {f7}
Orange: {fxl}
Yellow: {f5}
Green:  {f4}
Blue:   {f3}
Violet: {f1}""".format(**data))

        time.sleep(1.5)

except KeyboardInterrupt:
    as7343.set_illumination_led(False)
