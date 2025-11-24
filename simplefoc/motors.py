
from enum import Enum
import time
from .registers import parse_register, Register, SimpleFOCRegisters
from .motor import Motor
from .telemetry import Telemetry
import serial as ser
from rx import operators as ops, Observable
from simplefoc import FrameType, Frame
from .packets import ASCIIComms, BinaryComms, CANComms, ProtocolType


try:
    import can as python_can
except ImportError:
    print("WARNING: python-can not installed. Install with: pip install python-can if useing CAN communication.")
    python_can = None
    


def serial(port, baud, protocol=ProtocolType.binary):
    """ Create a serial connection to a SimpleFOC driver, and return a Motors instance to interact with it. 
        The connection is packet-based, and uses either ASCII or binary protocol.
        
        Note that the serial connection is not opened until you call motors.connect().
    
        @param port: the serial port to connect to
        @param baud: the baud rate to use
        @param protocol: the protocol to use (binary or ascii)
    """
    ser_conn = ser.Serial()
    ser_conn.port = port
    ser_conn.baudrate = baud
    comms = None
    if protocol == ProtocolType.binary:
        comms = BinaryComms(ser_conn)
    elif protocol == ProtocolType.ascii:
        comms = ASCIIComms(ser_conn)
    else:
        raise ValueError("Unknown protocol type")
    return Motors(comms)


def can(channel, target_address, bitrate=1000000, interface='socketcan'):
    """ Create a CAN connection to a SimpleFOC driver using CANCommander protocol.
        
        @param channel: CAN interface (e.g., 'can0')
        @param target_address: Target node address (0x00-0xFF)
        @param bitrate: CAN bitrate in bps (default 1000000)
        @param bustype: CAN bus type (default 'socketcan')
    """
    
    can_bus = python_can.interface.Bus(channel=channel, interface=interface, bitrate=bitrate)
    return Motors(CANComms(can_bus, target_address))


class Motors(object):
    """ SimpleFOC Motors class

        Used in packed-based communication, and provides a high-level interface to access motors, telemetry and
        to communicate with the driver through simple methods.
    
        Typically, you will get a Motors instance by calling packets.serial(port, baud)
        
        Once you have the Motors instance, you can get a Motor instance by calling motors.motor(motor_id).
        Motor ids are integers, starting from 0. If you have only one motor, you can ignore the motor_id parameter, 
        it is defaulted to 0.

        @param connection: the packet-based connection (ASCIIComms or BinaryComms) object
    """
    def __init__(self, connection):
        self.connection = connection
        self.current_motor = -1
        self._observable = self.connection.observable().pipe(
            ops.filter(lambda p: p.frame_type == FrameType.RESPONSE or p.frame_type == FrameType.ALERT),
            ops.do_action(self.__set_motor_id),
            ops.share()
        )
        self._observable.subscribe()

    def disconnect(self):
        self.connection.disconnect()

    def connect(self):
        self.connection.connect()

    def motor(self, motor_id:int=0) -> Motor:
        return Motor(self, motor_id)
    
    def set_register(self, motor_id:int, reg:int|str|Register, values):
        if not hasattr(values, "__len__"):
            values = [values]
        if not isinstance(reg, Register):
            reg = parse_register(reg)
        if reg==SimpleFOCRegisters.REG_MOTOR_ADDRESS:
            self.current_motor = values[0]      # optimistic
        elif self.current_motor != motor_id:
            self.connection.send_frame(Frame(frame_type=FrameType.REGISTER, register=SimpleFOCRegisters.REG_MOTOR_ADDRESS, values=[motor_id]))
            self.current_motor = motor_id       # optimistic
        self.connection.send_frame(Frame(frame_type=FrameType.REGISTER, register=reg, values=values, motor_id=motor_id))

    def set_register_with_response(self, motor_id:int, reg:int|str|Register, values, timeout=1.0):
        self.set_register(motor_id, reg, values)
        return self.get_response(motor_id, reg, timeout)

    def get_register(self, motor_id:int, reg:int|str|Register, timeout=None):
        if not isinstance(reg, Register):
            reg = parse_register(reg)
            
        if type(self.connection) is CANComms:
            
            if timeout is None:
                timeout = 1.0
                            
            result = {"value": None}
            def on_next(v):
                result["value"] = v
            # subscribe FIRST so we don't miss the response
            exp = self.expect_response(motor_id, reg, timeout)
            sub = exp.subscribe(on_next)
            
            try:
                # send the request
                self.connection.send_frame(Frame(frame_type=FrameType.REGISTER, register=reg, values=[], motor_id=motor_id))

                # wait for response
                start = time.time()
                while result["value"] is None:
                    if (time.time() - start) > timeout:
                        raise TimeoutError(
                            f"Timeout waiting for response for register {reg} on motor {motor_id}"
                        )
                    time.sleep(0.001)

                return result["value"]

            finally:
                sub.dispose()

        else:
            if self.current_motor != motor_id:
                self.connection.send_frame(Frame(frame_type=FrameType.REGISTER, register=SimpleFOCRegisters.REG_MOTOR_ADDRESS, values=[motor_id]))
                self.current_motor = motor_id    
            self.connection.send_frame(Frame(frame_type=FrameType.REGISTER, register=reg, values=[]))
            if timeout is not None:
                return self.get_response(motor_id, reg, timeout)
        
        
    def get_response(self, motor_id:int, reg:int|str|Register, timeout=1.0):
        self.reg_val = None
        return self.observable().pipe(
            ops.filter(lambda p: p.frame_type == FrameType.RESPONSE and p.motor_id == motor_id and p.register == reg),
            ops.filter(lambda p: p.values is not None and len(p.values) > 0),
            ops.first(),
            ops.map(lambda p: p.values if len(p.values) > 1 else p.values[0]),
            ops.timeout(float(timeout))
        ).run()
    

    def expect_response(self, motor_id:int, reg:int|str|Register, timeout=1.0) -> Observable:
        return self.observable().pipe(
            ops.filter(lambda p: p.frame_type == FrameType.RESPONSE and p.motor_id == motor_id and p.register == reg),
            ops.filter(lambda p: p.values is not None and len(p.values) > 0),
            ops.first(),
            ops.map(lambda p: p.values if len(p.values) > 1 else p.values[0]),
            ops.timeout(float(timeout))
        )
        
    
    def telemetry(self) -> Telemetry:
        return Telemetry(self)

    def observable(self) -> Observable:
        return self._observable
    
    def echo(self):
        return self.connection.echo()

    def console(self):
        return self.observable().pipe(
            ops.merge(self.echo())
        )
    
    def __set_motor_id(self, packet):
        if packet.frame_type == FrameType.RESPONSE:
            if packet.register == SimpleFOCRegisters.REG_MOTOR_ADDRESS:
                self.current_motor = packet.values[0]

            # Only override motor_id if it's ot already set (serial/binary canse)
            if not hasattr(packet, "motor_id"):
                packet.motor_id = self.current_motor
                
        return packet
