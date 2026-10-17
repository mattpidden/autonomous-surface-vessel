# Raspberry Pi Setup

This gets you to a headless Pi running ROS 2 that you control from your Mac over SSH (a remote terminal). It takes about 30–45 minutes, mostly waiting for downloads.

## 1. Flash the SD card (on your Mac)

1. Install **Raspberry Pi Imager** from [raspberrypi.com/software](https://www.raspberrypi.com/software/), or run `brew install --cask raspberry-pi-imager`.
2. Put the SD card in your Mac and open Imager.
   - **Device:** Raspberry Pi 4
   - **OS:** Other general-purpose OS → Ubuntu → **Ubuntu Server 24.04.x LTS (64-bit)**
   - **Storage:** your SD card
3. When it asks about **OS customisation**, click **Edit Settings**:
   - **Hostname:** `asv-pi4`
   - **Username and password:** your choice
   - **Wi-Fi:** your home network name and password, and country **GB**
   - **Services tab:** enable SSH. If you have an SSH key, choose "public-key authentication" and click "Run SSH-keygen" or add your key. Otherwise use your password.
4. Click **Write** and wait for it to finish and verify.

## 2. First boot

1. Put the card in the Pi and power it from a **5V 3A USB-C supply**: the official Pi supply, or a good phone charger. Use that for now rather than the boat's power converter.
2. **Wait 3–5 minutes.** The first boot sets everything up, including Wi-Fi.
3. Find the Pi's IP address. Look in your router's admin page for a device called `asv-pi4`, or run `arp -a` on your Mac.
4. Connect from your Mac's Terminal:
   ```bash
   ssh yourusername@<pi-ip-address>
   ```

## 3. Update it and make it easier to find

Run these on the Pi:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y avahi-daemon   # lets you use asv-pi4.local instead of the IP address
sudo reboot
```

After it reboots, you can connect with `ssh yourusername@asv-pi4.local`.

## 4. Install ROS 2 Jazzy

These are the official steps. Use **ros-base**, the version with no graphical tools, since the Pi has no screen.

```bash
# Allow the extra packages and tools ROS 2 needs
sudo apt install -y software-properties-common curl
sudo add-apt-repository -y universe

# Add the ROS 2 package source
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# Install ROS 2
sudo apt update && sudo apt upgrade -y
sudo apt install -y ros-jazzy-ros-base ros-dev-tools ros-jazzy-demo-nodes-cpp

# Load ROS 2 automatically in every terminal
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## 5. Test it

Open **two** SSH sessions to the Pi.

- In the first: `ros2 run demo_nodes_cpp talker`
- In the second: `ros2 run demo_nodes_cpp listener`

If the second window prints "I heard: Hello World…", ROS 2 is working.

## Next steps

- **Create a workspace** with `mkdir -p ~/usv_ws/src`. Your ROS packages go in there, and you can keep it in a git repo.
- **Camera:** Ubuntu needs extra setup for the Pi camera, using Raspberry Pi's own version of the camera software (libcamera). Tackle that when you get to vision.
- **Power saving:** turning off HDMI and Bluetooth, and Wi-Fi once you're on LTE, comes later, once everything works.
