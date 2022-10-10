import time
from as7343 import AS7343

as7343 = AS7343()

as7343.set_channels(18)

while True:
    results = list(as7343.read_fifo())
    print(len(results))
    if len(results) == 21:
        # Mask shift off trash byte
        results[6] >>= 8
        results[13] >>= 8
        results[20] >>= 8
        # Mask out reserved bits
        results[6] &= 0b10001111
        results[13] &= 0b10001111
        results[20] &= 0b10001111
        print("""
    FZ (B) {} FY (G) {} FXL (O/R) {} NIR {} VIS {} FD {} ASTATUS {}
    F2 (V) {} F3 (B) {} F4 (C) {} F6 (O) {} VIS {} FD {} ASTATUS {}
    F1 (V) {} F5 (Y) {} F7 (R) {} F8 (R) {} VIS {} FD {} ASTATUS {}
        """.format(*results))
    time.sleep(1.5)