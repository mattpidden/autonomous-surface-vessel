# Minimal MS8607 driver (pressure, temperature, humidity).
# The chip shows up as two I2C devices: 0x76 for pressure/temperature, 0x40 for humidity.
import time

PT_ADDRESS = 0x76
RH_ADDRESS = 0x40

PT_RESET = 0x1E
PT_PROM_READ = 0xA0
PT_CONVERT_D1 = 0x48  # pressure, oversampling 4096
PT_CONVERT_D2 = 0x58  # temperature, oversampling 4096
PT_ADC_READ = 0x00

RH_RESET = 0xFE
RH_MEASURE = 0xF5  # no-hold mode: start, wait, then read


class MS8607:
    def __init__(self, i2c):
        self.i2c = i2c
        self.i2c.writeto(PT_ADDRESS, bytes([PT_RESET]))
        self.i2c.writeto(RH_ADDRESS, bytes([RH_RESET]))
        time.sleep_ms(20)
        # Factory calibration coefficients C1..C6 stored on the chip
        self.c = [0] * 7
        for i in range(1, 7):
            data = self.i2c.readfrom_mem(PT_ADDRESS, PT_PROM_READ + i * 2, 2)
            self.c[i] = (data[0] << 8) | data[1]

    def _read_adc(self, command):
        self.i2c.writeto(PT_ADDRESS, bytes([command]))
        time.sleep_ms(10)
        data = self.i2c.readfrom_mem(PT_ADDRESS, PT_ADC_READ, 3)
        return (data[0] << 16) | (data[1] << 8) | data[2]

    def pressure_temperature(self):
        """(pressure in hPa, temperature in degrees C)."""
        c = self.c
        d1 = self._read_adc(PT_CONVERT_D1)
        d2 = self._read_adc(PT_CONVERT_D2)

        # Datasheet first- and second-order compensation
        dt = d2 - c[5] * 256
        temp = 2000 + dt * c[6] // (1 << 23)
        off = c[2] * (1 << 17) + c[4] * dt // (1 << 6)
        sens = c[1] * (1 << 16) + c[3] * dt // (1 << 7)

        if temp < 2000:
            t2 = 3 * dt * dt // (1 << 33)
            off2 = 61 * (temp - 2000) ** 2 // 16
            sens2 = 29 * (temp - 2000) ** 2 // 16
            if temp < -1500:
                off2 += 17 * (temp + 1500) ** 2
                sens2 += 9 * (temp + 1500) ** 2
        else:
            t2 = 5 * dt * dt // (1 << 38)
            off2 = 0
            sens2 = 0

        temp -= t2
        off -= off2
        sens -= sens2
        pressure = (d1 * sens // (1 << 21) - off) // (1 << 15)
        return pressure / 100, temp / 100

    def humidity(self, temperature):
        """Relative humidity in %, corrected using the temperature in degrees C."""
        self.i2c.writeto(RH_ADDRESS, bytes([RH_MEASURE]))
        time.sleep_ms(20)
        data = self.i2c.readfrom(RH_ADDRESS, 3)
        raw = ((data[0] << 8) | data[1]) & 0xFFFC
        rh = -6 + 125 * raw / 65536
        rh += (20 - temperature) * -0.18
        return min(max(rh, 0), 100)

    def read(self):
        """(pressure hPa, temperature C, humidity %)."""
        pressure, temperature = self.pressure_temperature()
        return pressure, temperature, self.humidity(temperature)
