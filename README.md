# Autonomous Surface Vessel (ASV) Project
A 3D-printed autonomous sailing surface vessel designed for marine data collection and experimentation in autonomous navigation. 

## Capabilities
- Autonomous waypoint navigation
- Sail and rudder control
- GPS based localisation
- IMU-based heading and motion estimation
- Wind-aware sailing and route planning
- Marine environmental data collection
- Georeferenced data logging
- Computer vision for surface obstacle detection
- Remote telemetry and mission monitoring
- Autonomous mission planning

## Parts

### Compute & control (£135.00)
- [x] [Raspberry Pi 4 4GB](https://thepihut.com/products/raspberry-pi-4-model-b?variant=20064052740158) | ✓ £96.00 | 4GB is plenty for headless ROS 2 + light vision. 
- [x] [SanDisk High Endurance 64GB microSD](https://www.amazon.co.uk/SanDisk-Endurance-Monitoring-Dashcams-MicroSDXC/dp/B07P3D6Y5B) | £24 | Made for continuous writing, so it suits all-day data logging.
- [x] [Pico](https://thepihut.com/products/pimoroni-pico-lipo-2) | ✓ £15.00 | Pimoroni Pico LiPo 2 (RP2350). USB-C, Qw/ST and SP/CE connectors.


### Navigation & comms (£88.60)
- [x] [Waveshare A7670E Cat-1](https://thepihut.com/products/a7670e-lte-cat-1-hat-for-raspberry-pi-2g-gsm-gprs) | ✓ £28.80 | LTE telemetry.
- [x] [IoT data SIM](TODO) | ~£10 | Low-data telemetry SIM.
- [x] [Adafruit BNO055 9-DoF IMU](https://thepihut.com/products/adafruit-9-dof-absolute-orientation-imu-fusion-breakout-bno055-stemma-qt-qwiic?variant=32209168597054&country=GB&currency=GBP) | ✓ £28.80 | Does sensor fusion on the chip and gives roll, pitch and turn rate
- [x] [STEMMA QT Cable x2](https://thepihut.com/products/stemma-qt-qwiic-jst-sh-4-pin-cable-100mm-long) | ✓ £2.00
- [x] [USB-C to USB-A cables x2](https://thepihut.com/products/usb-a-to-usb-c-cable-1m) for LTE hat and for Pi to Pico | ✓ £7.00
- [x] [USB GPS](https://www.amazon.co.uk/Receiver-Navigation-Notebook-Interface-DC3-3-5V/dp/B0BRQGZ4QV) | £14


### Vision (£39.60)
- [x] [Raspberry Pi Camera Module 3 Wide](https://thepihut.com/products/raspberry-pi-camera-module-3) | ✓ £33.60 | CSI, 120° view, autofocus, HDR. Uses less power than USB and works with the ROS 2 `camera_ros` package.
- [ ] [Clear Protectino Dome for camera](TODO) | ~£6
- [x] [Longer camera cable](https://thepihut.com/products/flex-cable-for-raspberry-pi-camera-or-display-18-457mm)


### Environmental sensors (£123.20)
- [x] [Pressure Humidity Temperature PHT Sensor](https://thepihut.com/products/adafruit-ms8607-pressure-humidity-temperature-pht-sensor) | ✓ £14.40 | Air temp/humidity/pressure. Mount it on deck in a vented, shaded housing. Can be dasiy changed into IMU sensor.
- [x] [Wind Speed & Direction Transmiter](https://www.amazon.co.uk/Ultrasonic-Direction-Sensor-Anemometer-Measurable/dp/B0H3613T5G) | £83
- [x] [RS485 to TTL adapter](https://www.amazon.co.uk/Converter-Direction-Compatible-Industrial-Automation/dp/B0GVQRYVNQ) | £5.4 | Check it supports 3.3V logic.
- [x] [TTL to 8pin cable](https://thepihut.com/products/8-pin-jst-sh-cable-sp-ce?variant=53798448431489) | ✓ £1.80 | Pick the JST-SH to DuPont version.


### Actuation (£102.40)
- [x] [12V Worm Gear Motor with Encoders x2](https://www.amazon.co.uk/Torque-Geared-Reduction-Encoder-Self-locking/dp/B07DG9QYPY) 30RPM for rudder and 10RPM for wing sail | £27 (£13.8 each)
- [x] [Motor driver](https://thepihut.com/products/dc-motor-driver-module-for-raspberry-pi-pico) | ✓ £14.40
- [x] [Power adapter for driver](https://thepihut.com/products/dc-dc-power-module-25w) £8.20
- [x] [Thruster motor](https://www.amazon.co.uk/ApisQueen-U2-Bi-Directional-ESC-Screw-Propellers/dp/B0C74CMXR9) | £62


### Power (£92.00)
- [x] [12V 12Ah LiFePO4 battery](https://www.amazon.co.uk/DCHOUSE-Trolling-Household-Appliances-Emergency/dp/B0CNP6Q28P) | £41.5 | 
- [x] [Battery Charger](https://www.amazon.co.uk/ECO-WORTHY-Lithium-LiFePO4-Automatic-Maintainer-black/dp/B0DGL4HKS6?th=1) | 36gbp
- [x] [Step down 12V to 5V for Pi](https://www.amazon.co.uk/DC-DC-Step-Converter-Type-C-Interface-as-shown-detailed-picture/dp/B0H7S63FXC) | £9
- [x] [On/off switch](https://www.amazon.co.uk/Joinfworld-Waterproof-Toggle-Mounting-Automotive/dp/B0G3982R8M) 10gbp


### Structure (£18.00)
- [ ] [Keel weights (lead)](https://www.claygame.co.uk/lead-shot-samples-pd378) | £18 for 2kg
- [ ] [2KG ABA Filament](https://uk.store.bambulab.com/products/abs-filament?id=41905581916220) £30



## Power budget (average draw at the battery)
| Load | Watts |
|---|---|
| Pi 4 headless + ROS 2 (after ~90% efficient 5V converter) | 3.5 |
| Camera + low-rate obstacle detection (runs part of the time) | 0.8 |
| Ultrasonic wind sensor (12V) | 0.6 |
| LTE Cat-1 telemetry | 0.5 |
| Rudder worm gear (self-locking, moves often) | 0.5 |
| Pico LiPo 2 | 0.15 |
| USB GPS | 0.15 |
| Sail worm gear (self-locking, moves rarely) | 0.15 |
| IMU, PHT sensor, motor driver idle | 0.1 |
| **Total** | **~6.5 W, ~155 Wh/day** |

A 12Ah LiFePO4 holds ~154Wh (~138Wh usable), which gives **~21h with no thruster use**. The thruster draws tens of watts, so every hour it runs costs several hours of endurance. To reach 24h, run the camera only near obstacles or in harbours, turn off Wi-Fi/Bluetooth/HDMI, or fit a larger battery if the weight budget allows. The wind sensor figure is typical for ultrasonic sensors, so check its datasheet.

## Software stack
**Raspberry Pi 4** (Ubuntu Server 24.04, headless, ROS 2 Jazzy)
- Localisation: `robot_localization` EKF fusing USB GPS (`nmea_navsat_driver`) with IMU heading from the Pico
- Planning: wind-aware sailing planner that turns waypoints into a course to steer and decides when to tack
- Vision: `camera_ros` + lightweight obstacle detection at a low frame rate
- Telemetry over LTE, and data logging with `rosbag2`

**Pimoroni Pico LiPo 2** (micro-ROS over USB serial, or a simple serial bridge if micro-ROS doesn't support the RP2350 yet)
- Reads the IMU and PHT sensor over I2C (Qw/ST) and the wind sensor over RS485/Modbus (SP/CE)
- Drives the rudder and sail worm gears to position using their encoders. Both are centred by hand at startup.
- Steers to the course from the Pi and trims the sail to the wind
- Sends the thruster ESC its PWM signal

## Assembly
- 3D print the hull in 3x1 sections with conectors
- Use acertone to bond together, then coat in epoxy
- Same for keel, which bolts into hull from inside
- Same for wing sail
- Use heat sets into the hull for modular plate system
- Design modular plate system to house all electronics
- Grease stuffed tubes for rudder and sail shafts
- Pole bolted to transom for Wind sensor, celluar arial, and IMU/PHT mounting 
- Lid with rubber seal and bolted down?
- On/off switch mounted on deck aft of sail