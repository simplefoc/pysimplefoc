#
# SimpleFOC Telemetry Tool
# Supports binary or ascii protocol types. Commander is not supported.
#
# Usage:
#   python simplefoc-telemetry.py --help
#
# Functions:
#   - Connect to SimpleFOC, configure and intitiate telemetry
#   - Dump telemetry data to stdout or specified file
#   - Format as Tabbed Columns, CSV, JSON or binary
#   - Stop after spedified conditions are met:
#     - Number of samples
#     - Time elapsed
#     - Absolute time
#   - Or continue until cancelled manually
#     - Auto-Reconnect to SimpleFOC
#   - Store telemetry to databases
#     - InfluxDB
#     - MQTT 
#

import argparse
import sys
import json
import simplefoc.packets as packets
from rx import operators as ops, Observable as rx
try:
    from paho.mqtt import client as mqtt_client
except ModuleNotFoundError:
    pass

parser = argparse.ArgumentParser(description='PySimpleFOC Telemetry Tool')
parser.add_argument('--baud', type=int, default=115200, help='Baud rate')
parser.add_argument('--type', choices=['binary', 'ascii'], type=str, default='binary', help='Protocol type')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
parser.add_argument('--motors', type=int, default='0', nargs='+', required=False, 
                    help='Motor IDs, use on multi-motor setups. Provide either a single value, or as many motor-ids as registers')
parser.add_argument('--downsample', type=int, help='Set telemetry downsample value on MCU', required=False)
parser.add_argument('--samples', type=int, help='Stop after this many samples', required=False)
parser.add_argument('--seconds', type=int, help='Stop after this many seconds', required=False)
parser.add_argument('--format', choices=['python', 'tabbed', 'csv', 'json', 'binary'], type=str, default='python', help='Output format')
parser.add_argument('--print', action='store_true', help='Print to stdout')
parser.add_argument('--output', type=str, help='Output to file')
parser.add_argument('--mqtt', type=str, help='MQTT server in the form: mqtt://user:pass@broker:port/topic?clientid=xyz', required=False)
parser.add_argument('--influx', type=str, help='InfluxDB server', required=False)
parser.add_argument('--nohup', type=bool, default=False, help='Don\'t stop telemetry')
parser.add_argument('--header', action='store_true', help='Print header at start of output')
parser.add_argument('--echo', type=str, help='Print command responses to stdout', default=False) # TODO implement
parser.add_argument('port', type=str, help='Serial port to use')
parser.add_argument('registers', type=str, help='Set registers to monitor on MCU', nargs='*')
args = parser.parse_args()

joinchar = '\t' if args.format == 'tabbed' else ',' if args.format == 'csv' else ' '

def format_frame(frame, format):
    if format == 'python':
        return str(frame)
    if frame.frame_type == packets.FrameType.HEADER:
        strs = [f'{mot}:{reg.short_name()}' for (reg, mot) in frame.registers] \
            if all(mot == 0 for (reg, mot) in frame.registers) \
                else [reg.short_name() for (reg, mot) in frame.registers]
        if format == 'tabbed' or format == 'csv':
            return strs.join(joinchar)
        elif format == 'json':
            return json.dumps(strs)
    elif frame.frame_type == packets.FrameType.TELEMETRY:
        if format == 'tabbed' or format == 'csv':
            return joinchar.join(str(x) for x in frame.values)
        elif format == 'json':
            return json.dumps(frame.values)
        # elif format == 'binary':
        #     pass # todo implement
    return str(frame) # in all other cases, return the string representation of the python object


motors = None
match args.type:
    case 'binary':
        motors = packets.serial(args.port, args.baud)
    case 'ascii':
        motors = packets.serial(args.port, args.baud, protocol=packets.ProtocolType.ascii)
    case _:
        print("Invalid protocol type.")
        sys.exit(1)

if args.verbose:
    print(f"Connected to {args.port} at {args.baud} baud.")


def signalhandler(signum):
    motors.disconnect()
    if args.verbose:
        print("Serial port closed.")


telemetry = motors.telemetry()

motors.connect()

if len(args.registers) >= 0:
    pass # TODO set registers and get header

pipeline = []

if args.header:
    pipeline.append(ops.skip_while(lambda p: p.frame_type != packets.FrameType.HEADER))

if args.samples is not None and args.samples > 0:
    numsamples = args.samples + 1 if args.header else 0
    pipeline.append(ops.take(numsamples))

if args.seconds is not None and args.seconds > 0:
    pipeline.append(ops.take_until_with_time(args.seconds))

pipeline.append(ops.map(lambda p: format_frame(p, args.format)))

if args.format == 'json':
    pipeline.append(ops.start_with('['))
    pipeline.append(ops.concat(rx.just(']')))

frames = telemetry.observable().pipe(*pipeline)

if args.output is not None:
    with open(args.output, 'w') as file:
        frames.subscribe(on_next=lambda f: file.write(f, '\n'), on_completed=lambda: file.close())
else:
    args.print = True       # if no output files given then print to stdout

if args.print:
    frames.subscribe(lambda f: print(f))

if args.mqtt is not None:
    if mqtt_client is None:
        print("MQTT library not found, please install paho-mqtt.")
    else:
        pass # todo connect to MQTT server
        topic = 'xyz' # todo parse topic from args.mqtt
        frames.subscribe(on_next=lambda f: mqtt_client.publish(topic, f), on_completed=lambda: mqtt_client.disconnect())

if args.influx is not None:
    pass # TODO connect to InfluxDB server

if len(args.registers) <= 0:
    telemetry.request_header()

if args.downsample is not None:
    telemetry.set_downsample(args.downsample)
# TODO like this the telemetry has to be running already, or downsample must be provided, otherwise it won't start... 
#    should we set a default value for downsample if its not provided? or should we check first?    

frames.run()               # wait for telemetry to stop or ctrl-c

if args.nohup==False:
    telemetry.stop()

motors.disconnect()
if args.verbose:
    print("Serial port closed.")
