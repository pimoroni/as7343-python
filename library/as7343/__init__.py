"""Library for the AS7343 Visble Light Spectral Sensor."""
import time
import math
import struct

from i2cdevice import Device, Register, BitField, _int_to_bytes
from i2cdevice.adapter import Adapter, LookupAdapter, U16ByteSwapAdapter

__version__ = '0.0.1'


class AGCFDGainAdapter(Adapter):
    """Convert the AGC gain value.

    2^N (0 = 0.5x)"""

    def _decode(self, value):
        if value == 0:
            return 0.5
        return 2 << int(value)

    def _encode(self, value):
        if value == 0.5:
            return 0
        return value.bit_length() - 2


class AGAINAdapter(Adapter):
    """Convert the AGC gain value.

    GAINx = 1 << (n - 1)"""

    def _decode(self, value):
        if value == 0:
            return 0.5
        return 1 << int(value - 1)

    def _encode(self, value):
        if value == 0.5:
            return 0
        return int(value).bit_length() & 0x1f


class ASTEPAdapter(Adapter):
    """Convert the ASTEP value.
    0 = 2.78us
    n = 2.78us x (n + 1)
    65535 = don't use!
    """

    def _decode(self, value):
        return (value + 1) * 2.78

    def _encode(self, value):
        return int((value - 2.78) / 2.78) & 0xfffe


class WTIMEAdapter(Adapter):
    """Convert the WTIME value.
    0 = 2.78ms
    n = 2.78ms x (n + 1)
    range: 2.87 to 711.68 ms
    """

    def _decode(self, value):
        return (value + 1) * 2.78

    def _encode(self, value):
        return int((value - 2.78) / 2.78) & 0xff


class LEDDriveAdapter(Adapter):
    def _decode(self, value):
        return (value * 2  + 4) & 0xff

    def _encode(self, value):
        return int((value - 4) / 2)


class FloatAdapter(Adapter):
    """Convert a 4 byte register set into a float."""

    def _decode(self, value):
        b = _int_to_bytes(value, 4)
        return struct.unpack('>f', bytearray(b))[0]


class Result6Channel:
    """Store a 6-channel AS7343 result."""
    def __init__(self, fz, fy, fxl, nir, vis):
        self.fz = fz        # Blue
        self.fy = fy        # Green
        self.fxl = fxl      # Orange
        self.nir = nir      # Near Infra-red
        self.vis = vis      # Visible

    def __iter__(self):  # noqa D107
        for c in ['fz', 'fy', 'fxl', 'nir', 'vis']:
            yield getattr(self, c)


class Result12Channel(Result6Channel):
    """Store a 12-channel AS7343 result."""
    def __init__(self, fz, fy, fxl, nir, vis, f2, f3, f4, f6):
        Result6Channel.__init__(self, fz, fy, fxl, nir, vis)

        self.f2 = f2        # Violet
        self.f3 = f3        # Blue/Cyan
        self.f4 = f4        # Cyan
        self.f6 = f6        # Orange/Red

    def __iter__(self):  # noqa D107
        for c in Result6Channel.__iter__(self):
            yield c
        for c in [ 'f2', 'f3', 'f4', 'f6']:
            yield getattr(self, c)


class Result18Channel(Result12Channel):
    """Store a 12-channel AS7343 result."""
    def __init__(
        self,
        fz, fy, fxl, nir, vis,
        f2, f3, f4, f6,
        f1, f5, f7, f8):

        Result12Channel.__init__(
            self,
            fz, fy, fxl, nir, vis,
            f2, f3, f4, f6)

        self.f1 = f1        # Violet
        self.f5 = f5        # Yellow/Green
        self.f7 = f7        # Red
        self.f8 = f8        # Red

    def __iter__(self):  # noqa D107
        for c in Result12Channel.__iter__(self):
            yield c
        for c in ['f1', 'f5', 'f7', 'f8']:
            yield getattr(self, c)


class AS7343:
    def __init__(self, i2c_dev=None):
        self._as7343 = Device(0x39, bit_width=8, registers=(
            # BANK 1
            Register('AUXID', 0x58, fields=(
                BitField('AUXID', 0b00001111),   # Auxiliary Identification (0b0000)
            )),
            Register('REVID', 0x59, fields=(
                BitField('REVID', 0b00000111),   # Revision ID (0b000)
            )),
            Register('ID', 0x5A, fields=(
                BitField('ID', 0b11111111),      # Part Number (0b10000001)
            )),
            Register('CFG12', 0x66, fields=(
                BitField('SP_TH_CH', 0b00000111),  # Spectral Threshold Channel
            )),

            # BANK 0
            Register('ENABLE', 0x80, fields=(
                BitField('FDEN', 0b01000000),     # Flicker Detection Enable
                BitField('SMUXEN', 0b00010000),   # SMUX Enable
                BitField('WEN', 0b00001000),      # Wait Enable
                BitField('SP_EN', 0b00000010),    # Spectral Measurement Enable
                BitField('PON', 0b00000001)       # Power On
            )),
            Register('ATIME', 0x81, fields=(
                BitField('ATIME', 0xFF),          # Integration Time
                                                  # Number of integration steps from 0 to 255
                                                  # (ATIME + 1) x (ASTEP + 1) x 2.78us
                                                  # ADCfs = (ATIME + 1) x (ASTEP + 1)
            )),
            Register('ASTEP', 0xD4, fields=(
                # Integration Time Step Size
                # 0 = 2.87us
                # n 2.87us x (n + 1)
                BitField('ASTEP', 0xFFFF, adapter=ASTEPAdapter()),
            ), bit_width=16),
    
            # Spectral Measurement Wait Time
            # 0 = 1 cycle = 2.78ms
            # n = 2.78ms x (n + 1)
            Register('WTIME', 0x83, fields=(
                BitField('WTIME', 0xFF, adapter=WTIMEAdapter()),    
            )),
            Register('SP_TH', 0x84, fields=(
                BitField('SP_TH_L', 0xFFFF0000),  # Spectral Low Threshold
                BitField('SP_TH_H', 0x0000FFFF)   # Spectrail High Threshold
            ), bit_width=8 * 4),
            Register('STATUS', 0x93, fields=(
                BitField('ASAT', 0b10000000),     # Spectral Saturation (if ASIEN set)
                BitField('AINT', 0b00001000),     # Spectral Channel Interrupt (if SP_IEN set)
                BitField('FINT', 0b00000100),     # FIFO Buffer Interrupt
                BitField('SINT', 0b00000001)      # System Interrupt
            )),
            Register('ASTATUS', 0x94, fields=(
                BitField('ASAT_STATUS', 0b10000000),  # Saturation Status
                BitField('AGAIN_STATUS', 0b00000111)  # Gain Status
            )),
            Register('DATA', 0x95, fields=(
                BitField('DATA_0', 0xFFFF << (17 * 8 * 2)),
                BitField('DATA_1', 0xFFFF << (16 * 8 * 2)),
                BitField('DATA_2', 0xFFFF << (15 * 8 * 2)),
                BitField('DATA_3', 0xFFFF << (14 * 8 * 2)),
                BitField('DATA_4', 0xFFFF << (13 * 8 * 2)),
                BitField('DATA_5', 0xFFFF << (12 * 8 * 2)),
                BitField('DATA_6', 0xFFFF << (11 * 8 * 2)),
                BitField('DATA_7', 0xFFFF << (10 * 8 * 2)),
                BitField('DATA_8', 0xFFFF << (9 * 8 * 2)),
                BitField('DATA_9', 0xFFFF << (8 * 8 * 2)),
                BitField('DATA_10', 0xFFFF << (7 * 8 * 2)),
                BitField('DATA_11', 0xFFFF << (6 * 8 * 2)),
                BitField('DATA_12', 0xFFFF << (5 * 8 * 2)),
                BitField('DATA_13', 0xFFFF << (4 * 8 * 2)),
                BitField('DATA_14', 0xFFFF << (3 * 8 * 2)),
                BitField('DATA_15', 0xFFFF << (2 * 8 * 2)),
                BitField('DATA_16', 0xFFFF << (2 * 8 * 2)),
                BitField('DATA_17', 0xFFFF << (0 * 8 * 2)),
            ), bit_width=8 * 2 * 18),  # 18 data fields, * 2 bytes each
            Register('STATUS2', 0x90, fields=(
                BitField('AVALID', 0b01000000),     # Spectral Data Valid
                BitField('ASAT_DIG', 0b00010000),   # Digital Saturation
                BitField('ASAT_ANA', 0b00001000),   # Analog Saturation
                BitField('FDSAT_ANA', 0b00000010),  # Flicker Analog Saturation
                BitField('FDSAT_DIG', 0b00000001)   # Flicker Digital Saturation
            )),
            Register('STATUS3', 0x91, fields=(
                BitField('INT_SP_H', 0b00100000),   # Spectral Above High Threshold
                BitField('INT_SP_L', 0b00010000)    # Spectral Below Low Threshold
            )),
            Register('STATUS5', 0xBB, fields=(
                BitField('SINT_FD', 0b00001000),    # Flicker Detect Interrupt (if SIEN_FD set)
                BitField('SINT_SMUX', 0b00000100)   # SMUX Operation Interrupt (SMUX exec finished)
            )),
            Register('STATUS4', 0xBC, fields=(
                BitField('FIFO_OV', 0b10000000),    # FIFO Buffer Overflow
                BitField('OVTEMP', 0b00100000),     # Over Temperature
                BitField('FD_TRIG', 0b00010000),    # Flicker Detetc Trigger Error
                BitField('SD_TRIG', 0b00000100),    # Spectral Trigger Error
                BitField('SAI_ACT', 0b00000010),    # Sleep After Interrupt Active
                BitField('INT_BUSY', 0b00000001)    # Initialization Busy (1 for ~300us after power on)
            )),
            Register('CFG0', 0xBF, fields=(
                BitField('LOW_POWER', 0b00100000),  # Low Power Idle
                BitField('REG_BANK', 0b00010000),   # 0 - Register 0x80 and above
                                                    # 1 - Register 0x20 to 0x7f
                BitField('WLONG', 0b00000100)       # Increases WTIME by factor of 16
            )),
            Register('CFG1', 0xC6, fields=(
                # Spectral Engines Gain Setting
                # 0 = 0.5x, # 1 = 1x, 2 = 2x, 12 = 2048x
                # GAINx = 1 << (n - 1)
                BitField('AGAIN', 0b00011111, adapter=AGAINAdapter()),
            )),
            Register('CFG3', 0xC7, fields=(
                BitField('SAI', 0b00010000),    # Sleep After Interrupt (turn off osc after interrupt)
            )),
            Register('CFG6', 0xF5, fields=(
                # SMUS Command To Exec
                # 0 - ROM code init
                # 1 - Read SMUX conf to RAM
                # 2 - Write SMUX conf from RAM
                # 3 - Reserved
                BitField('SMUX_CMD', 0b00011000, adapter=LookupAdapter({
                    'ROM_init': 0,
                    'Read_SMUX': 1,
                    'Write_SMUX': 2
                })),
            )),
            Register('CFG8', 0xC9, fields=(
                # Fifo Threshold
                BitField('FIFO_TH', 0b11000000, adapter=LookupAdapter({
                    1: 0b00,
                    4: 0b01,
                    8: 0b10,
                    16: 0b11
                })),
            )),
            Register('CFG9', 0xCA, fields=(
                BitField('SIEN_FD', 0b01000000),    # System Interrupt Flicker Detection
                BitField('SIEN_SMUX', 0b00010000)   # System Interrupt SMUX Operation
            )),
            Register('CFG10', 0x65, fields=(
                BitField('FD_PERS', 0b00000111),    # Flicker Detect Persistence
                                                    # Number of results that must be diff before status change
            )),
            Register('PERS', 0xCF, fields=(
                BitField('APERS', 0b00001111),
            )),
            Register('GPIO', 0x6B, fields=(
                BitField('GPIO_INV', 0b00001000),    # Invert GPIO output
                BitField('GPIO_IN_EN', 0b00000100),  # Enable GPIO input
                BitField('GPIO_OUT', 0b00000010),    # GPIO Output
                BitField('GPIO_IN', 0b00000001)      # GPIO Input
            )),
            Register('CFG20', 0xD6, fields=(
                BitField('FD_FIFO_8b', 0b10000000),  # Enable 8bit FIFO mode for Flicker Detect (FD_TIME < 256)
                # Auto channel read-out
                BitField('auto_SMUX', 0b01100000, adapter=LookupAdapter({
                    6: 0b00,
                    # '': 0b01,  ' reserved
                    12: 0b10,
                    18: 0b11
                }))
            )),
            Register('LED', 0xCD, fields=(
                BitField('LED_ACT', 0b10000000),   # External LED (LDR) Control
                # External LED drive strength  (N - 4) >> 1
                BitField('LED_DRIVE', 0b01111111, adapter=LEDDriveAdapter())
            )),
            Register('AGC_GAIN_MAX', 0xD7, fields=(
                # Flicker Detection AGC Gain Max
                # Max = 2^N (0 = 0.5x)
                BitField('AGC_FD_GAIN_MAX', 0b11110000, adapter=AGCFDGainAdapter()),
            )),
            Register('AZ_CONFIG', 0xDE, fields=(
                BitField('AT_NTH_ITERATION', 0b11111111),  # Auto-zero Frequency
                                                           # 0 NEVER (not recommended)
                                                           # n = every n integration cycles
                                                           # 255 = only before first measurement cycle
            )),
            Register('FD_TIME_1', 0xE0, fields=(  # Flicker Detection Integration Time
                BitField('FD_TIME', 0b11111111),  # FD_TIME [7:0] (do not change if FDEN = 1 & PON = 1)
            )),
            Register('FD_TIME_2', 0xE2, fields=(
                # Flicker Detect Gain - 0 = 0.5x, 1 = 1x, 2 = 2x, 12 = 2048x
                BitField('FD_GAIN', 0b11111000, adapter=AGAINAdapter()),
                BitField('FD_TIME', 0b00000111)   # FD_TIME [10:8] (do not change if FDEN = 1 & PON = 1)
            )),
            Register('FD_CFG0', 0xDF, fields=(
                BitField('FIFO_WRITE_FD', 0b10000000),   # Write flicker raw data to FIFO (1 byte per sample)
            )),
            Register('FD_STATUS', 0xE3, fields=(
                BitField('FD_VALID', 0b00100000),        # Flicker Detection Valid
                BitField('FD_SAT', 0b00010000),          # Flicker Detection Saturated
                BitField('FD_120HZ_VALID', 0b00001000),  # Flicker Detection 120HZ Valid
                BitField('FD_100HZ_VALID', 0b00000100),  # Flicker Detection 100HZ Valid
                BitField('FD_120HZ', 0b00000010),        # Flicker Detected at 120HZ
                BitField('FD_100HZ', 0b00000001)         # Flicker Detected at 100HZ
            )),
            Register('INTERNAB', 0xF9, fields=(
                BitField('ASIEN', 0b10000000),   # Saturation Interrupt Enable
                BitField('SP_IEN', 0b00001000),  # Spectral Interrupt Enable
                BitField('FIEN', 0b00000100),    # FIFO Buffer Interrupt Enable
                BitField('SIEN', 0b00000001)     # System Interrupt Enable
            )),
            Register('CONTROL', 0xFA, fields=(
                BitField('SW_RESET', 0b00001000),   # Software Reset
                BitField('SP_MAN_AZ', 0b00000100),  # Spectral Manual Autozero
                BitField('FIFO_CLR', 0b00000010),   # FIFO Buffer Clear
                BitField('CLEAR_SAI_ACT', 0b00000001)  # Clear Sleep-After-Interrupt
            )),
            # FIFO Buffer Included Channels
            Register('FIFO_MAP', 0xFC, fields=(
                BitField('FIFO_WRITE_CH5_DATA', 0b01000000),
                BitField('FIFO_WRITE_CH4_DATA', 0b00100000),
                BitField('FIFO_WRITE_CH3_DATA', 0b00010000),
                BitField('FIFO_WRITE_CH2_DATA', 0b00001000),
                BitField('FIFO_WRITE_CH1_DATA', 0b00000100),
                BitField('FIFO_WRITE_CH0_DATA', 0b00000010),
                BitField('FIFO_WRITE_ASTATUS', 0b00000001)
            )),
            # FIFO Buffer Level
            Register('FIFO_LVL', 0xFD, fields=(
                BitField('FIFO_LVL', 0xFF),
            ), read_only=True),
            # FIFO Buffer Data
            Register('FDATA', 0xFE, fields=(
                BitField('FDATA', 0xFFFF, adapter=U16ByteSwapAdapter()),
            ), bit_width=16, read_only=True)
        ))

        # TODO : Integrate into i2cdevice so that LookupAdapter fields can always be exported to constants
        # Iterate through all register fields and export their lookup tables to constants
        for register in self._as7343.registers:
            register = self._as7343.registers[register]
            for field in register.fields:
                field = register.fields[field]
                if isinstance(field.adapter, LookupAdapter):
                    for key in field.adapter.lookup_table:
                        value = field.adapter.lookup_table[key]
                        name = 'AS7343_{register}_{field}_{key}'.format(
                            register=register.name,
                            field=field.name,
                            key=key
                        ).upper()
                        locals()[name] = key

        self.soft_reset()

        self._as7343.set('ENABLE',
            PON=True)

        self.bank_select(0)  # For registers 0x80 and above

        self.set_channels(6)

        # The actual total wait time will be multiplies by the number of channel cycles
        # 6 channels completes in 1 cycle (WTIME)
        # 12 channels completes in 2 cycles (WTIME * 2)
        # 18 channels completes in 3 cycles (WTIME * 3)
        # WTIME must be large enough to accomodate integration time and any other sundries
        self._as7343.set('WTIME', WTIME=500)  # time (in ms) between readings

        # Interation time comprises a time (in us) called "ASTEP" for some reason,
        # and a repeat count called "ATIME".
        # The total integration time is ASTEP * ATIME.
        self._as7343.set('ATIME', ATIME=1)       # integration time multiplier, basically
        self._as7343.set('ASTEP', ASTEP=50000)   # integration time (us)

        self._as7343.set('LED',
            LED_ACT=False,
            LED_DRIVE=4)

        # Make sure all channels are written into the FIFO
        # By default the output from channels is *NOT* written so you can
        # (even in 18ch mode) select the channels you're interested in.
        self._as7343.set('FIFO_MAP',
            FIFO_WRITE_CH5_DATA=True,
            FIFO_WRITE_CH4_DATA=True,
            FIFO_WRITE_CH3_DATA=True,
            FIFO_WRITE_CH2_DATA=True,
            FIFO_WRITE_CH1_DATA=True,
            FIFO_WRITE_CH0_DATA=True,
            FIFO_WRITE_ASTATUS=True)

        self._as7343.set('ENABLE',
            FDEN=False,
            WEN=True,
            SMUXEN=True,
            SP_EN=True)

    def bank_select(self, bank=0):
        """Set the AS7343 bank select register."""
        self._as7343.set('CFG0', REG_BANK=bank)

    def soft_reset(self):
        """Set the soft reset register bit of the AS7343."""
        self._as7343.set('CONTROL', SW_RESET=1)
        # Polling for the state of the reset flag does not work here
        # since the fragile virtual register state machine cannot
        # respond while in a soft reset condition
        # So, just wait long enough for it to reset fully...
        time.sleep(2.0)

    def set_channels(self, channel_count):
        """Set the multiplexer mode of the AS7343.

        Set the number of physical channels multiplexed into the output FIFO.

        :param mode: Mode. One of 6, 12 or 18.

        """
        if channel_count not in (6, 12, 18):
            raise ValueError("Invalid channel count. Expected 6, 12 or 18.")

        self._channel_count = channel_count
        self._as7343.set('CFG20', auto_SMUX=channel_count)

    def read_fifo(self):
        while self._as7343.get('FIFO_LVL').FIFO_LVL > 0:
            result = self._as7343.get('FDATA').FDATA
            yield result





    def get_calibrated_values(self, timeout=10):
        """Return an instance of CalibratedValues containing the 6 spectral bands."""
        t_start = time.time()
        while self._as7343.get('CONTROL').data_ready == 0 and (time.time() - t_start) <= timeout:
            pass
        data = self._as7343.get('CALIBRATED_DATA')
        return CalibratedValues(data.r, data.o, data.y, data.g, data.b, data.v)

    def set_gain(self, gain):
        """Set the gain amount of the AS7343.

        :param gain: gain multiplier, one of 1, 3.7, 16 or 64

        """
        self._as7343.set('CONTROL', gain_x=gain)

    def set_measurement_mode(self, mode):
        """Set the AS7343 measurement mode.

        :param mode: 0-3

        """
        self._as7343.set('CONTROL', measurement_mode=mode)

    def set_integration_time(self, time_ms):
        """Set the AS7343 sensor integration time in milliseconds.

        :param time_ms: Time in milliseconds from 0 to ~91

        """
        self._as7343.set('INTEGRATION_TIME', ms=time_ms)

    def set_illumination_led_current(self, current):
        """Set the AS7343 illumination LED current in milliamps.

        :param current: Value in milliamps, one of 12.5, 25, 50 or 100

        """
        self._as7343.set('LED_CONTROL', illumination_current_limit_ma=current)

    def set_indicator_led_current(self, current):
        """Set the AS7343 indicator LED current in milliamps.

        :param current: Value in milliamps, one of 1, 2, 4 or 8

        """
        self._as7343.set('LED_CONTROL', indicator_current_limit_ma=current)

    def set_illumination_led(self, state):
        """Set the AS7343 illumination LED state.

        :param state: True = On, False = Off

        """
        self._as7343.set('LED_CONTROL', illumination_enable=state)

    def set_indicator_led(self, state):
        """Set the AS7343 indicator LED state.

        :param state: True = On, False = Off

        """
        self._as7343.set('LED_CONTROL', indicator_enable=state)

    def get_version(self):
        """Get the hardware type, version and firmware version from the AS7343."""
        version = self._as7343.get('VERSION')
        return version.hw_type, version.hw_version, version.fw_version