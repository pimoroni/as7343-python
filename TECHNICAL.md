# Overview

Uses six 16-bit ADCs switched over the 5x5 arrya via SMUX
and then output sequentially into the 18-entry, 16-bit data registers.

# Channels

Values for AGAIN 1024x, Integration Time: 27.8ms.

Approximate colours from Figure 11.

| Chan | From | To   | Min  | Typ  | Max  | Colour |
|------|------|------|------|------|------|--------|
| F1   | 396  | 408  | 4311 | 5749 | 7186 | Violet |
| F2   | 408  | 448  | 1317 | 1756 | 2196 | Violet |
| FZ   | 428  | 480  | 1627 | 2169 | 2711 | Blue   |
| F3   | 448  | 500  | 577  | 770  | 962  | Blue/Cyan |
| F4   | 500  | 534  | 2356 | 3141 | 3926 | Cyan   |
| FY   | 534  | 593  | 2810 | 3747 | 4684 | Green  |
| F5   | 531  | 594  | 1180 | 1574 | 1967 | Yellow/Green  |
| FXL  | 593  | 628  | 3582 | 4776 | 5970 | Orange |
| F6   | 618  | 665  | 2502 | 3336 | 4170 | Oraneg/Red    |
| F7   | 685  | 715  | 4095 | 5435 | 6774 | Red    |
| F8   | 715  | 766  | 648  | 864  | 1080 | Red    |
| NIR  | 849  | 903  | 7936 | 10581 | 13226 | Infra-Red  |
|------|------|------|------|-------|-------|------------|