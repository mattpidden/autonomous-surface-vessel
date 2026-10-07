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

### Compute & control (£)
- [x] [Raspberry Pi 4 4GB](https://thepihut.com/products/raspberry-pi-4-model-b?variant=20064052740158) | ✓ £95.60 | 4GB is plenty for headless ROS 2 + light vision. 
- [ ] [SanDisk High Endurance 64GB microSD](https://www.amazon.co.uk/SanDisk-Endurance-Monitoring-Dashcams-MicroSDXC/dp/B07P3D6Y5B) | ~£24 | Made for continuous writing, so it suits all-day data logging.
- [x] [Pico](https://thepihut.com/products/pimoroni-pico-lipo-2) 15gbp


### Navigation & comms (£)
- [x] [Waveshare A7670E Cat-1](https://thepihut.com/products/a7670e-lte-cat-1-hat-for-raspberry-pi-2g-gsm-gprs) | ~£29 | LTE telemetry and GPS HAT.
- [ ] [IoT data SIM](TODO) | ~£10 | Low-data telemetry SIM.
- [x] [Adafruit BNO085 9-DoF IMU](https://thepihut.com/products/adafruit-9-dof-absolute-orientation-imu-fusion-breakout-bno055-stemma-qt-qwiic?variant=32209168597054&country=GB&currency=GBP) | ✓ £28.40 | Does sensor fusion on the chip and gives roll, pitch and turn rate
- [x] [STEMMA QT Cable x2](https://thepihut.com/products/stemma-qt-qwiic-jst-sh-4-pin-cable-100mm-long)
- [x] [USB-C to USB-A cables x2](https://thepihut.com/products/usb-a-to-usb-c-cable-1m) for LTE hat and for Pi to Pico


### Vision ()
- [x] [Raspberry Pi Camera Module 3 Wide](https://thepihut.com/products/raspberry-pi-camera-module-3) | ✓ £33.60 | CSI, 120° view, autofocus, HDR. Uses less power than USB and works with the ROS 2 `camera_ros` package.


### Environmental sensors (£48.10)
- [x] [Adafruit BME280](https://thepihut.com/products/adafruit-ms8607-pressure-humidity-temperature-pht-sensor) | ✓ £14.40 | Air temp/humidity/pressure. Mount it on deck in a vented, shaded housing. Can be dasiy changed into IMU sensor.



- [ ] [Wind Direction Transmiter](https://thepihut.com/products/rs485-wind-direction-transmitter) | TODO I think i NEED ultrasonic sensor
- [ ] [RS485 to usb](TODO)


### Actuation (£)
- [ ] [Rudder motor](TODO)
- [ ] [Wing sail motor](TODO)
- [ ] [Thruster motor](TODO)
- [ ] [Various drivers](TODO)


### Power (£120.40)
- [ ] [12V 12Ah LiFePO4 battery](TODO) | ~£50 | About 23h on the budget below. See the power budget for how to reach 24h+.
- [ ] [Battery Charger](TODO)
- [ ] [Step down 12V to 5V for Pi](TODO)


### Structure (£35)
- [ ] [Keel weights (lead)](https://www.claygame.co.uk/lead-shot-samples-pd378) | ~£18 for 2kg



## Power budget (average draw at the battery)
| Load | Watts |
|---|---|

| **Total** | **~W, ~ Wh/day** |


## Software stack
- Ubuntu Server 24.04 (headless) + ROS 2 Jazzy, which has ready-built ROS 2 packages for Pi 5 on this OS
- micro-ROS on the Pico 2 (actuators, watchdog that centres the rudder and stops the thruster if the Pi goes silent)
- `robot_localization` EKF fusing GNSS, compass and IMU; Nav2 or a custom sailing planner for waypoints
