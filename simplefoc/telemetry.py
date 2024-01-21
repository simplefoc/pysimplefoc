#
# Functions and classes to help with SimpleFOC telenetry output
#

from rx import operators as ops
from .registers import SimpleFOCRegisters, parse_register, Register
from simplefoc import FrameType


MAX_TELEMTRY_IDS = 8


class Telemetry:
    """ SimpleFOC Telemetry class

        Used to configure and start/stop telemetry output from the driver.

        Typically, you will get a Telemetry instance by calling motors.telemetry()

        
    """
    def __init__(self, motors):
        self.motors = motors
        self.motors.connection.observable().pipe(
            ops.filter(lambda p: p.frame_type == FrameType.HEADER)
        ).subscribe(self.__update_header)
        self.headers = [ None ] * MAX_TELEMTRY_IDS
        self._telemetry = self.motors.connection.observable().pipe(
            ops.filter(lambda p: p.frame_type == FrameType.TELEMETRY),
            ops.filter(lambda p: self.headers[p.telemetryid] is not None),
            ops.map(lambda p: self.motors.connection.parse_telemetry(p, self.headers[p.telemetryid])),
            ops.share()
        )
        self._telemetry_ctrl = 0

    def set_registers(self, registers, motors=None, telemetryid=0):
        if motors is None:
            motors = [0] * len(registers)
        if len(registers) != len(motors):
            raise Exception("registers and motors must be the same length")
        if telemetryid < 0 or telemetryid >= MAX_TELEMTRY_IDS:
            raise Exception("telemetryid must be between 0 and {}".format(MAX_TELEMTRY_IDS-1))
        if telemetryid != self._telemetry_ctrl:
            self.motors.set_register(self.motors.current_motor, SimpleFOCRegisters.REG_TELEMETRY_CTRL, telemetryid)
            self._telemetry_ctrl = telemetryid
        values = [len(registers)]
        for i in range(0, len(registers)):
            r = registers[i]
            if motors is not None:
                values.append(motors[i])
            else:
                values.append(0)
            if not isinstance(r, Register):
                r = parse_register(r)
            values.append(r.id)
        self.motors.set_register(self.motors.current_motor, SimpleFOCRegisters.REG_TELEMETRY_REG, values)

#    def set_period(self, period=0.25):
#        pass # todo implement period as a register?

    def set_downsample(self, downsample=100, telemetryid=0):
        if telemetryid < 0 or telemetryid >= MAX_TELEMTRY_IDS:
            raise Exception("telemetryid must be between 0 and {}".format(MAX_TELEMTRY_IDS-1))
        if telemetryid != self._telemetry_ctrl:
            self.motors.set_register(0, SimpleFOCRegisters.REG_TELEMETRY_CTRL, telemetryid)
            self._telemetry_ctrl = telemetryid        
        self.motors.set_register(self.motors.current_motor, SimpleFOCRegisters.REG_TELEMETRY_DOWNSAMPLE, downsample)

    def set_telemety_ctrl(self, telemetryid=0):
        if telemetryid < 0 or telemetryid >= MAX_TELEMTRY_IDS:
            raise Exception("telemetryid must be between 0 and {}".format(MAX_TELEMTRY_IDS-1))
        if telemetryid != self._telemetry_ctrl:
            self.motors.set_register(self.motors.current_motor, SimpleFOCRegisters.REG_TELEMETRY_CTRL, telemetryid)
            self._telemetry_ctrl = telemetryid

    def header(self, telemetryid=0):
        return self.headers[telemetryid]
    
    def fetch_headers(self):
        self.motors.get_register(0, SimpleFOCRegisters.REG_TELEMETRY_REG)

    #
    # Get an observable of the telemetry data
    #
    def observable(self):
        return self._telemetry
    
    def listen(self, listener_func):
        self.observable().subscribe(listener_func)

    def __update_header(self, packet):
        self.headers[packet.telemetryid] = packet
