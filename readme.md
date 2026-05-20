# HTC Tracker Python Wrapper

This repository allows you to collect and stream tracker data from HTC Tracker (both 2.0 or 3.0 versions) usign Python.

## Software setup
Follow the steps below in case you do not use the HTC head-mounted display.

* Download [Steam and Steam VR](https://store.steampowered.com/app/250820/SteamVR/?l=italian)
* In your file manager, go to the global SteamVR settings file: C:\Program Files (x86)\Steam\steamapps\common\SteamVR\resources\settings\default.vrsettings
* Back up the global default.vrsettings, then open it in a text editor and set the following:
```
"requireHmd" : false,
"forcedDriver": "null"
"activateMultipleDrivers" : true,
```
* Then, in your file manager, go to the null driver settings file:
C:\Program Files (x86)\Steam\steamapps\common\SteamVR\drivers\null\resources\settings\default.vrsettings
* Back up the null driver default.vrsettings, then open it in a text editor and set the following:
```
"enable" : true,
```

## Scripting setup
In order to run python scripts, at least `Python version 3.9` is required.
All the scripts are based on the [Triad OpenVR Python Wrapper](https://github.com/TriadSemi/triad_openvr).


## Usage

The `htc_streamer_class` class allows you to set up the trackers and the order of trackers to retrieve data and stream it over UDP to a specified IP and port.

**Configuration**
- Edit `config.json` to list your devices. Each entry must contain `name`, `type` (one of `Tracker`, `HMD`, `Controller`, `Tracking Reference`) and the device `serial` as reported by SteamVR. The wrapper maps physical tracker serials to the logical names used in the code (for example `hand`, `forearm`, `arm`, `chest`, `controlatHand`).

**Running**
1. Run an example emitter:

```
python examples/udp_emitter_5trackers.py
```

2. Or use the class directly in your script:

```python
from htc_streamer_class import htc_streamer_class

# Choose modality (mod1..mod5), target IP/port and sample_rate (seconds)
streamer = htc_streamer_class(modality="mod1", sender_ip="192.168.1.135", sender_port=5005, sample_rate=1/90)
streamer.stream_to_udp()
```

**Modality**
- `mod1` — `['hand']`
- `mod2` — `['hand','forearm']`
- `mod3` — `['hand','forearm','arm']`
- `mod4` — `['hand','forearm','arm','chest']`
- `mod5` — all (default list from `ID_tracker` in code)

**UDP packet format**
- The Python streamer packs data using `struct.pack("=IfI{n}d")` where the fields are:
  - `start_message` (int)
  - `timestamp` (float, seconds since start)
  - `n_trackers_selected` (int)
  - then `n` double values (7 values per tracker): `[x, y, z, qw, qx, qy, qz]` for each tracker in the configured `ID_tracker` order.

When unpacking, expect 7 doubles per tracker. The `triad_openvr` helper returns pose as `[x,y,z,r_w,r_x,r_y,r_z]` which corresponds to `[x,y,z,qw,qx,qy,qz]`.

**Notes & tips**
- If a configured tracker is not present or reports no pose, the streamer will insert seven zeros for that tracker and print a warning message.
- The example `examples/udp_emitter_5trackers.py` modifies `sys.path` so you can run it from the examples folder without installing the package.
- On Windows, ensure SteamVR is running and the null/forced drivers and `requireHmd` settings (see Software setup) are configured if you don't have an HMD attached.
- To change the order or logical names of devices, update `config.json` device `name` values to match the `ID_tracker` list used by `htc_streamer_class`.