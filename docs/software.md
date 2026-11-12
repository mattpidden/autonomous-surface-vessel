# Software stack

**Raspberry Pi 4** (Ubuntu Server 24.04, headless, ROS 2 Jazzy)
- Localisation: `robot_localization` EKF fusing USB GPS (`nmea_navsat_driver`) with IMU heading from the Pico
- Planning: wind-aware sailing planner that turns waypoints into a course to steer and decides when to tack
- Vision: `camera_ros` + lightweight obstacle detection at a low frame rate
- Telemetry over LTE, and data logging with `rosbag2`
- `ssh user@asv-pi4.local`

**Pimoroni Pico LiPo 2** (micro-ROS over USB serial, or a simple serial bridge if micro-ROS doesn't support the RP2350 yet)
- Reads the IMU and PHT sensor over I2C (Qw/ST) and the wind sensor over RS485/Modbus (SP/CE)
- Drives the rudder and sail worm gears to position using their encoders. Both are centred by hand at startup.
- Steers to the course from the Pi and trims the sail to the wind
- Sends the thruster ESC its PWM signal

