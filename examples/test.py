import time
from as7343 import AS7343

as7343 = AS7343()

as7343.set_channels(18)

while True:
    results = as7343.get_data()

    if results is not None:
        print("    FZ (B) {fz: 5d} | FY (G) {fy: 5d} | FXL (O/R) {fxl: 5d} | NIR    {nir: 5d} | VIS(TL) {vis_tl: 5d} | VIS(BR) {vis_br: 5d} | SAT {saturated} | GAIN {gain:02d}x".format(**results[0]))
        print("    F2 (V) {f2: 5d} | F3 (B) {f3: 5d} | F4  (C)   {f4: 5d} | F6 (O) {f6: 5d} | VIS(TL) {vis_tl: 5d} | VIS(BR) {vis_br: 5d} | SAT {saturated} | GAIN {gain:02d}x".format(**results[1]))
        print("    F1 (V) {f1: 5d} | F5 (Y) {f5: 5d} | F7  (R)   {f7: 5d} | F8 (R) {f8: 5d} | VIS(TL) {vis_tl: 5d} | VIS(BR) {vis_br: 5d} | SAT {saturated} | GAIN {gain:02d}x".format(**results[2]))
        print("")

    time.sleep(1.5)
