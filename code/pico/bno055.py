# Minimal BNO055 driver (IMU with on-chip sensor fusion), I2C address 0x28.
import time
import struct

ADDRESS = 0x28

CHIP_ID = 0x00
PAGE_ID = 0x07
ACCEL_DATA = 0x08
GYRO_DATA = 0x14
EULER_DATA = 0x1A
QUAT_DATA = 0x20
TEMP = 0x34
CALIB_STAT = 0x35
OPR_MODE = 0x3D
PWR_MODE = 0x3E

MODE_CONFIG = 0x00
MODE_NDOF = 0x0C  # full fusion: accel + gyro + magnetometer -> absolute heading


class BNO055:
    def __init__(self, i2c, address=ADDRESS):
        self.i2c = i2c
        self.address = address
        if self._read_u8(CHIP_ID) != 0xA0:
            raise OSError("BNO055 not found at 0x%02x" % address)
        self._write_u8(OPR_MODE, MODE_CONFIG)
        time.sleep_ms(25)
        self._write_u8(PWR_MODE, 0x00)  # normal power
        self._write_u8(PAGE_ID, 0x00)
        self._write_u8(OPR_MODE, MODE_NDOF)
        time.sleep_ms(20)

    def _read_u8(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def _write_u8(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def _read_vector(self, reg, count, scale):
        data = self.i2c.readfrom_mem(self.address, reg, count * 2)
        return tuple(v / scale for v in struct.unpack("<%dh" % count, data))

    def euler(self):
        """(heading, roll, pitch) in degrees."""
        return self._read_vector(EULER_DATA, 3, 16)

    def quaternion(self):
        """(w, x, y, z), unitless."""
        return self._read_vector(QUAT_DATA, 4, 1 << 14)

    def gyro(self):
        """(x, y, z) turn rate in degrees per second."""
        return self._read_vector(GYRO_DATA, 3, 16)

    def accel(self):
        """(x, y, z) in m/s^2, including gravity."""
        return self._read_vector(ACCEL_DATA, 3, 100)

    def temperature(self):
        """Chip temperature in degrees C."""
        return struct.unpack("b", bytes([self._read_u8(TEMP)]))[0]

    def calibration(self):
        """(system, gyro, accel, mag), each 0 (uncalibrated) to 3 (fully calibrated)."""
        s = self._read_u8(CALIB_STAT)
        return (s >> 6) & 3, (s >> 4) & 3, (s >> 2) & 3, s & 3
