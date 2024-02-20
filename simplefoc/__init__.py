from enum import Enum
import time


class Direction(Enum):
  CCW = -1
  UNKNOWN = 0
  CW = 1


class TorqueControlType(Enum):
  voltage            = 0x00
  dc_current         = 0x01
  foc_current        = 0x02


class MotionControlType(Enum):
  torque            = 0x00
  velocity          = 0x01
  angle             = 0x02
  velocity_openloop = 0x03
  angle_openloop    = 0x04


class FOCModulationType(Enum):
  SinePWM            = 0x00
  SpaceVectorPWM     = 0x01
  Trapezoid_120      = 0x02
  Trapezoid_150      = 0x03


class FOCMotorStatus(Enum):
  motor_uninitialized = 0x00
  motor_initializing  = 0x01
  motor_uncalibrated  = 0x02
  motor_calibrating   = 0x03
  motor_ready         = 0x04
  motor_error         = 0x08
  motor_calib_failed  = 0x0E
  motor_init_failed   = 0x0F


class FrameType(Enum):
    REGISTER = 'R'
    RESPONSE = 'r'
    TELEMETRY = 'T'
    HEADER = 'H'
    SYNC = 'S'
    ALERT = 'A'



class Frame(object):
    def __init__(self, frame_type, register=None, values=None, alert=None, telemetryid=None, registers=None, motors=None, motor_id=None, header=None, timestamp=None):
        self.frame_type = frame_type
        if register is not None:
          self.register = register
        if values is not None:
          self.values = values
        if alert is not None:
          self.alert = alert
        if telemetryid is not None:
          self.telemetryid = telemetryid
        if registers is not None:
          self.registers = registers
        if motors is not None:
          self.motors = motors
        if motor_id is not None:
          self.motor_id = motor_id
        if header is not None:
          self.header = header
        if timestamp is not None:
          self.timestamp = timestamp
        else:
          self.timestamp = time.time()

    def __repr__(self): # TODO prettify this output
        return self.__dict__.__str__()

    def __str__(self):
        val = self.frame_type.value
        if hasattr(self, 'register'):
          val += str(self.register.id)
        if hasattr(self, 'values'):
          val += str(self.values)
        return val