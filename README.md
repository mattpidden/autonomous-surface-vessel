# Autonomous Surface Vessel

A 3D-printed autonomous boat for coastal data collection, running **ROS 2** on a Raspberry Pi with a Pico for real-time control. V1 is motor-driven; a wing sail follows in V2.

<p align="center">
  <img src="docs/images/cad-hero.jpg" alt="CAD render of the hull and keel" width="720">
</p>

| | |
|---|---|
| **Hull** | ~750 × 250 mm scow, printed in ABS sections, epoxy-coated |
| **Keel** | Printed fin with ~2 kg lead ballast, bolted through the hull |
| **Compute** | Raspberry Pi 4 (ROS 2 Jazzy) + Pico LiPo 2 (MicroPython) |
| **Sensing** | GPS, 9-DoF IMU, wind, pressure/temp/humidity, camera |
| **Comms & power** | LTE telemetry, 12.8 V 12 Ah LiFePO4 |

## System architecture

The Pico runs the fast control loop and the Pi runs ROS 2: localisation, planning, vision and telemetry.

```mermaid
flowchart LR
    subgraph Pi["Raspberry Pi 4 · ROS 2 Jazzy"]
        EKF["Localisation EKF"]
        PLAN["Planner"]
        VIS["Vision"]
        TEL["Telemetry + logging"]
    end
    subgraph Pico["Pico LiPo 2 · control loop"]
        CTRL["Heading control"]
    end
    GPS["GPS"] --> EKF
    CAM["Camera"] --> VIS
    SENS["IMU · wind · PHT"] --> Pico
    Pico <-- USB serial --> Pi
    PLAN -- course --> CTRL
    CTRL --> RUD["Rudder"]
    CTRL --> THR["Thruster"]
    TEL <--> LTE["LTE"]
```

## Development log

### Sep 2026 · Concept and parts
Chose the hardware and sized the battery from a power budget. → [Parts list](docs/parts-list.md)

### Oct 2026 · Hull shape iterations
Printed scale models and tested each for stability, ending in a scow bow for stability and internal space.

<p align="center">
  <img src="docs/images/hull-design-iterations.jpg" alt="Five printed scale hull models, from first design to final scow hull with keel" width="720">
</p>

<p align="center">
  <img src="docs/images/hull-stability-tests.jpg" alt="Stills from stability tests of hull versions 1, 2 and 3" width="600"><br>
  <sub>Stability tests: <a href="blog/hullv1stabiltytest.MP4">v1</a> · <a href="blog/hullv2stabilitytest.MOV">v2</a> · <a href="blog/hullv3stabilitytest.mov">v3</a></sub>
</p>

### Oct 2026 · Full-size hull, keel and mounts
Designed the bolted keel joint, rudder, and the thruster, motor and battery mounts.

<p align="center">
  <img src="docs/images/cad-side.jpg" alt="Side profile of the hull and keel" width="48%">
  <img src="docs/images/cad-underside.jpg" alt="Underside view of the hull and keel" width="40%">
</p>

### Oct 2026 · Electronics bring-up
Set up ROS 2 on the Pi and MicroPython on the Pico, and wrote [IMU](code/pico/bno055.py) and [PHT](code/pico/ms8607.py) drivers from the datasheets. → [Pi setup](docs/pi-setup.md) · [Pico setup](docs/pico-setup.md)

### Nov 2026 · Hull top and first prints
Finalised dimensions, added the hatch and section joints, and printed the bow and keel.

<p align="center">
  <img src="docs/images/bow-timelapse.gif" alt="Timelapse of the bow section printing" width="48%">
  <img src="docs/images/keel-timelapse.gif" alt="Timelapse of the keel printing" width="48%">
</p>

<!--
Template for new entries:

### Mon YYYY · Title
One or two sentences.

<p align="center">
  <img src="docs/images/your-image.jpg" alt="Description" width="720">
</p>
-->

## Roadmap

**V1: motor-driven**
- [x] Hull, keel and rudder CAD
- [x] Pi + ROS 2 and Pico bring-up
- [ ] Print, bond and epoxy the hull, pour keel ballast
- [ ] Pico ↔ Pi bridge publishing sensor topics
- [ ] Rudder and thruster control
- [ ] First float and trials
- [ ] Autonomous waypoint missions

**V2: sailing**
- [ ] Wing sail and sail control
- [ ] Wind-aware route planning

## Docs

[Parts list & power budget](docs/parts-list.md) · [Software stack](docs/software.md) · [Assembly notes](docs/assembly.md) · [Pi setup](docs/pi-setup.md) · [Pico setup](docs/pico-setup.md)
