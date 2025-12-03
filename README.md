# SimpleFOC Python API

:warning: Under active development and not fully tested

:warning: API may change until v1.0.0 is released

:warning: not available on PyPI for installation via pip until 1.0.0 is released


This python library provides easy control of SimpleFOC from a desktop PC or other environment running python3.



![](https://github.com/runger1101001/pysimplefoc/assets/7306964/0f40461c-47e1-4494-a50f-89fde83da85b)



Note: Python API v0.0.4 is designed for use with SimpleFOC v2.3.3 or later

Features:

- Serial connections to SimpleFOC drivers
- **CAN bus connections via CANCommander protocol**
  > Important: CAN support requires python-can package and a USB dongle that supports it (ex. SocketCAN). 
- Control motors via Commander protocol
- Telemetry based on SimpleFOC monitoring abstraction
- Control motors via packet based protocol based on SimpleFOC Drivers Registers abstraction
- Access motor Telemetry via SimpleFOC Drivers Telemetry abstraction
- Data streams based on reactive observables, for easy processing of telemetry
- Compatibility with (local) Jupyter notebooks
- CLI-tools: command line utilities for working with simplefoc
- Examples

## Setup PC side

1. Install python dependencies:

```
pip install pyserial rx python-can
```
or, on Debian:
```
sudo apt install python3-serial python3-rx
pip install python-can
```

2. Install PySimpleFOC:

```
pip install simplefoc
```

:warning: Until the release to PyPI you cannot install pysimplefoc via pip. You can still use it: check it out from GitHub, and then create symlink (windows: directory junction) from inside your project to the `simplefoc` folder of pysimplefoc.

3. Set up your serial connection to the driver.

   **OR** set up your CAN bus connection (requires CAN hardware interface):
   ```bash
   # Linux SocketCAN setup
   sudo ip link set can0 type can bitrate 1000000
   sudo ip link set can0 up
   ```

4. Decide on protocol to use: Commander, Packets (Text/Binary), or **CAN**

5. Write and run some python code (see our [examples](./examples/))

## Setup Driver side

On the arduino (driver) side, you will need appropriate firmware to enable the communcation between the driver and the python program on the PC.

Depending on your protocol choices, the firmware needs to be written in different ways. Also, because people generally use their motors in the context of specific projects, you may need to *extend* the communication protocol with message types specific to your use case.

To get you started, take a look at the examples in the examples in the [arduino](./examples/arduino/) directory.

These examples include a generic setup that should work on many MCUs. If you've already used SimpleFOC you should find the code quite easy to understand. 

You will have to adapt the pins defined in the examples to match the connections of your setup, then you can compile and flash the firmware to your driver.

Typically a firmware adapted for python control should initialize everything with sensible default values (sensor, driver and motor), initialize communications according to the chosen protocol, and then disable the motor and wait for control input. The examples are structured in this way.

## CLI tools usage

The library comes with a few ready-to-use command line tools, you can find them in the [utilities](./utilities/) folder.

### simplefoc-cli

:warning: *Work in progress*

Send commands to the driver directly from the command line. Supports all the protocols and various command line options.

```plain
usage: simplefoc-cli.py [-h] [-b BAUD] [-m MOTORID] [-v] [-t {commander,binary,ascii}] port commands [commands ...]

PySimpleFOC Command Line Interface

positional arguments:
  port                  Serial port to use
  commands              One or more commands or register=value pairs, separated by spaces

options:
  -h, --help            show this help message and exit
  -b BAUD, --baud BAUD  Baud rate
  -m MOTORID, --motorid MOTORID
                        Motor ID (a number for binary or ascii protocol types, a letter for commander protocol type), default is M
  -v, --verbose         Verbose output
  -t {commander,binary,ascii}, --type {commander,binary,ascii}
                        Protocol type, default is commander
```

### simplefoc-telemetry

:warning: *Work in progress*

Dump telemetry data from serial to a variety of different formats.

```plain
usage: simplefoc-telemetry.py [-h] [--baud BAUD] [--type {binary,ascii}] [--verbose] [--motors MOTORS [MOTORS ...]] [--downsample DOWNSAMPLE] [--samples SAMPLES] [--seconds SECONDS] [--format {python,tabbed,csv,json,binary}] [--print] [--output OUTPUT] [--mqtt MQTT] [--influx INFLUX] [--nohup NOHUP] [--header] [--echo ECHO] port [registers ...]

PySimpleFOC Telemetry Tool

positional arguments:
  port                  Serial port to use
  registers             Set registers to monitor on MCU

options:
  -h, --help            show this help message and exit
  --baud BAUD           Baud rate
  --type {binary,ascii}
                        Protocol type
  --verbose             Verbose output
  --motors MOTORS [MOTORS ...]
                        Motor IDs, use on multi-motor setups. Provide either a single value, or as many motor-ids as registers
  --downsample DOWNSAMPLE
                        Set telemetry downsample value on MCU
  --samples SAMPLES     Stop after this many samples
  --seconds SECONDS     Stop after this many seconds
  --format {python,tabbed,csv,json,binary}
                        Output format
  --print               Print to stdout
  --output OUTPUT       Output to file
  --mqtt MQTT           MQTT server in the form: mqtt://user:pass@broker:port/topic?clientid=xyz
  --influx INFLUX       InfluxDB server
  --nohup NOHUP         Don't stop telemetry
  --header              Print header at start of output
  --echo ECHO           Print command responses to stdout
```


## Library usage

### Serial Communication (Commander protocol)

Using the python API is quite simple, the following examples show use of the 'commander' protocol:

```python
import simplefoc

commander = simplefoc.commander.serial("COM1", 115200)
commander.connect()

motor = commander.full_control('M')
motor.set_target(10)
```

### CAN Bus Communication (CANCommander protocol)

For CAN bus communication using the CANCommander protocol:

```python
import simplefoc.can as can
from simplefoc import MotionControlType, TorqueControlType

# Connect to CAN bus
motors = can.can_bus(
    interface='can0',           # CAN interface name
    target_address=0x05        # SimpleFOC driver's address
)
motors.connect()

# Get motor and control it
motor = motors.motor(0)
motor.set_mode(MotionControlType.torque, TorqueControlType.voltage)
motor.enable()
motor.set_target(2.0)

# Read motor state
velocity = motor.get_velocity()
angle = motor.get_angle()
```

See [examples/can/README.md](examples/can/README.md) for detailed CAN setup and usage.

### Common Motor Control

Various easy to use methods are pre-defined to interact with the motor:

```python
motor.set_limits(max_voltage=12.0, max_current=1.0, max_velocity=20.0)
motor.set_mode(MotionControlType.torque, TorqueControlType.voltage)
motor.enable()
```

But you can also just send commands as strings, anything Commander will understand on the driver side:

```python
commander.send_command('ME0')
```

Often, in python we will be interested in processing the telemetry data from the motor. Commander supports telemetry via the SimpleFOC motor monitoring, but you have to let the python side know which values are being sent:

```python
motor.set_monitoring(SimpleFOCRegisters.REG_ANGLE, SimpleFOCRegisters.REG_VELOCITY)
motor.start_monitoring()
```

The telemetry stream is a reactive observable to which you can subscribe:

```python
motor.telemetry().subscribe(lambda x: print(x))
```

## Jupyter notebooks

Jupyter Notebooks (see [jupyter.org](https://jupyter.org) for more information) are a great way to run experiments involving SimpleFOC and visualizing the results.

Because of the need for local serial port access, you have to install and run jupyter on your PC and can't use the cloud version. Don't worry, it's easy to install.

See the [jupyter](./jupyter/) folder for some examples to get you up and running.

## Further reading

For more usage examples, help and documentation, please consult:

- Our [documentation](./docs/)
- Our [examples](./examples/)
- Our [discord's](https://discord.com/invite/kWBwuzY32n) #python channel
