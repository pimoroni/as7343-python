F1 = 5749
F2 = 1756
FZ = 2169
F3 = 770
F4 = 3141
FY = 3747
F5 = 1574
FXL = 4776
F6 = 3336
F7 = 5435
F8 = 864
NIR = 10581

vals = [F1, F2, FZ, F3, F4, FY, F5, FXL, F6, F7, F8, NIR]

m = max(vals)

print(m)

for v in vals:
    print(f"{m / v:.02f}")
