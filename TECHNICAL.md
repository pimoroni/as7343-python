# Overview

Uses six 16-bit ADCs switched over the 5x5 array via SMUX
and then output sequentially into the 18-entry, 16-bit data registers.

# Channels

Values for AGAIN 1024x, Integration Time: 27.8ms.

Irradiance responsivity values from figure 8.

Approximate colours from Figure 11.

|------|------|------|------|-------|-------|------------|
| Chan | From | To   | Min  | Typ   | Max   | Colour     |
|------|------|------|------|-------|-------|------------|
| F1   | 395  | 415  | 4311 | 5749  | 7186  | Violet     |
| F2   | 415  | 435  | 1317 | 1756  | 2196  | Violet     |
| FZ   | 440  | 460  | 1627 | 2169  | 2711  | Blue       |
| F3   | 465  | 485  | 577  | 770   | 962   | Blue/Cyan  |
| F4   | 506  | 525  | 2356 | 3141  | 3926  | Cyan       |
| FY   | 545  | 565  | 2810 | 3747  | 4684  | Green      |
| F5   | 540  | 550  | 1180 | 1574  | 1967  | Yellow/Grn |
| FXL  | 590  | 610  | 3582 | 4776  | 5970  | Orange     |
| F6   | 630  | 650  | 2502 | 3336  | 4170  | Orange/Red |
| F7   | 680  | 700  | 4095 | 5435  | 6774  | Red        |
| F8   | 735  | 745  | 648  | 864   | 1080  | Red        |
| NIR  | 845  | 855  | 7936 | 10581 | 13226 | Infra-Red  |
|------|------|------|------|-------|-------|------------|