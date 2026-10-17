# Prints live readings from the IMU and the PHT sensor once a second.
# Needs bno055.py and ms8607.py saved on the Pico.
from machine import I2C, Pin
import time

from bno055 import BNO055
from ms8607 import MS8607

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
imu = BNO055(i2c)
pht = MS8607(i2c)

while True:
    heading, roll, pitch = imu.euler()
    sys_cal, gyro_cal, accel_cal, mag_cal = imu.calibration()
    pressure, temperature, humidity = pht.read()

    print("heading %6.1f  roll %6.1f  pitch %6.1f  | cal sys%d gyr%d acc%d mag%d"
          % (heading, roll, pitch, sys_cal, gyro_cal, accel_cal, mag_cal))
    print("pressure %7.2f hPa  temp %5.2f C  humidity %5.1f %%"
          % (pressure, temperature, humidity))
    print()
    time.sleep(1)
