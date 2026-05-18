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
All the scripts are based on the [Triad OpenVR Python Wrapper](https://github.com/TriadSemi/triad_openvr), moreover, the requirements are listed in the `requirements.txt` file.