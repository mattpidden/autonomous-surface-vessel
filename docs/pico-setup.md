# Pico Setup

Start with **MicroPython** on the Pico. It's the quickest way to check your sensors and motors work, and you can edit code straight on the board with no compiling. You can move to C/micro-ROS later if you want.

## 1. Download the firmware (on your Mac)

Pimoroni doesn't publish a build specifically for the Pico LiPo 2. Their **Pico Plus 2** build is a match: the two boards' pin definitions in the Pico SDK are identical, including the SP/CE pins (GP32/33), the LED, the memory and the flash size.

Download **`pimoroni_pico_plus2-v1.29.0-micropython.uf2`** from [Pimoroni's v1.29.0 release](https://github.com/pimoroni/pimoroni-pico-rp2350/releases/tag/v1.29.0).

Don't use the plain `rpi_pico2` build. It doesn't support GP32 and above, so it can't use the SP/CE port needed for the wind sensor.

## 2. Flash it

1. **Hold the BOOT button** on the Pico, plug its USB-C cable into your **Mac**, then let go.
2. A drive called **RP2350** appears in Finder.
3. Drag the `.uf2` file onto it. The drive disappears and the Pico restarts running MicroPython.

## 3. Connect and test (on the Mac)

Install **[Thonny](https://thonny.org)**, which is the simplest option. In the bottom-right corner, choose **MicroPython (Raspberry Pi Pico)**. If you'd rather use VS Code, the **MicroPico** extension does the same job.

**Test 1: blink the LED.** Type into the console:

```python
from machine import Pin
import time
led = Pin(25, Pin.OUT)
for _ in range(10):
    led.toggle()
    time.sleep(0.5)
```

**Test 2: find the sensors.** Unplug the Pico, plug the IMU and PHT chain into its **Qw/ST** port, plug the Pico back in, then run:

```python
from machine import I2C, Pin
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
print([hex(a) for a in i2c.scan()])
```

You should see **`['0x28', '0x40', '0x76']`**: 0x28 is the BNO055, and 0x40 and 0x76 are the MS8607. If one is missing, check that the cable is pushed fully into its socket.

**Startup:** anything you save to the Pico as **`main.py`** runs automatically every time it powers on. That's how it will run on the boat.

## 4. Connect it to the Pi

Once it works on the Mac, plug the Pico into the Pi's USB. Then, on the Pi:

```bash
ls /dev/ttyACM*                     # should show /dev/ttyACM0
sudo usermod -aG dialout $USER      # allow your user to access the serial port
```

**Log out and back in** so the permission change applies. Then test it:

```bash
sudo apt install -y pipx && pipx ensurepath
pipx install mpremote
mpremote connect /dev/ttyACM0 repl  # opens the Pico's Python console. Exit with Ctrl+]
```

This uses `pipx` rather than `pip`, because Ubuntu 24.04 blocks installing Python packages system-wide with `pip`.

**Tip:** write and test the Pico code from your Mac while you're developing; it's much quicker. Only move it to the Pi once you're building the full system.

## Next steps

1. Read real data from the BNO055 and MS8607. There are MicroPython drivers for both.
2. Have the Pico send readings to the Pi over USB serial, e.g. one line of JSON per reading.
3. Write a small ROS 2 node on the Pi that reads those lines and publishes them as topics.
