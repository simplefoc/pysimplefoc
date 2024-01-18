
SIZES = {
    'b': 1,
    'i': 4,
    'f': 4 
}

class Register:
    """ 
        Register class 
        Don't create this class directly, use SimpleFOCRegisters.add_register() instead

        name: str
        id: int
        read_types: list of chars b, i, f  - empty list means read not supported
        write_types: list of chars b, i, f - empty list means write not supported

        A register may return or accept multiple values of different types. For this reason the read_types and write_types
        are lists of chars, where each char represents a type. The type chars are:
            b: unsigned byte
            i: unsigned int
            f: float
    """
    def __init__(self, name, id, read_types, write_types):
        self.name = name
        self.id = id
        self.read_types = read_types
        self.write_types = write_types

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        if isinstance(other, Register):
            return self.id == other.id
        if isinstance(other, int):
            return self.id == other
        if isinstance(other, str):
            return self.name == other
        return False
    
    def __hash__(self):
        return hash(self.id)
    
    def __int__(self):
        return self.id

    def read_size(self):
        return sum([SIZES[t] for t in self.read_types])
    
    def write_size(self):
        return sum([SIZES[t] for t in self.write_types])

    def short_name(self):
        self.name[4:] if self.name.startswith('REG_') else self.name


class SimpleFOCRegisters(object):
    """ SimpleFOCRegisters class - static singleton class for all registers
        
        This class is a singleton, and implements a kind of Enum like behaviour for the available registers.
        Its not an actual Enum to enable dynamic creation of registers for when users want to extend it with
        their own registers.

        Access registers like this:
            reg = SimpleFOCRegisters.REG_STATUS
            reg = SimpleFOCRegisters.by_id(0x00)
            reg = parse_register('REG_STATUS')
            reg = parse_register('STATUS')

        Add registers like this:
            SimpleFOCRegisters.add_register('REG_MY_REGISTER', 0x80, ['f'], ['f'])

    """
    @classmethod
    def add_register(cls, name, id, read_types, write_types):
        if getattr(cls, name, None) is not None:
            raise Exception("Register {} already exists".format(name))
        for n in cls.__dict__:
            r = cls.__dict__[n]
            if isinstance(r, Register) and r.id == id:
                raise Exception("Can't add register {}, the id {} already exists as: {}".format(name, id, n))
        setattr(cls, name, Register(name, id, read_types, write_types))

    def by_id(id:int):
        for k in SimpleFOCRegisters.__dict__:      # TODO improve this
            r = SimpleFOCRegisters.__dict__[k]
            if isinstance(r, Register) and r.id == id:
                return r
        print("WARNING: Register id {} not found".format(id))
        return None

    REG_STATUS = Register('REG_STATUS',0x00,['b'],[])
    REG_MOTOR_ADDRESS = Register('REG_MOTOR_ADDRESS',0x01,['b'],['b'])
    REG_REPORT = Register('REG_REPORT',0x02,[],[])
    REG_ENABLE_ALL = Register('REG_ENABLE_ALL',0x03,[],['b'])
    REG_ENABLE = Register('REG_ENABLE',0x04,['b'],['b'])
    REG_CONTROL_MODE = Register('REG_CONTROL_MODE',0x05,['b'],['b'])
    REG_TORQUE_MODE = Register('REG_TORQUE_MODE',0x06,['b'],['b'])
    REG_MODULATION_MODE = Register('REG_MODULATION_MODE',0x07,['b'],['b'])

    REG_TARGET = Register('REG_TARGET',0x08,['f'],['f'])
    REG_ANGLE = Register('REG_ANGLE',0x09,['f'],[])
    REG_POSITION = Register('REG_POSITION',0x10,['i', 'f'],[])
    REG_VELOCITY = Register('REG_VELOCITY',0x11,['f'],[])
    REG_SENSOR_ANGLE = Register('REG_SENSOR_ANGLE',0x12,['f'],[])

    REG_TELEMETRY_REG = Register('REG_TELEMETRY_REG',0x1A,[],[])
    REG_TELEMETRY_CTRL = Register('REG_TELEMETRY_CTRL',0x1B,['b'],['b'])
    REG_TELEMETRY_DOWNSAMPLE = Register('REG_TELEMETRY_DOWNSAMPLE',0x1C,['i'],['i'])
    REG_ITERATIONS_SEC = Register('REG_ITERATIONS_SEC',0x1D,['i'],[])

    REG_VOLTAGE_Q = Register('REG_VOLTAGE_Q',0x20,['f'],[])
    REG_VOLTAGE_D = Register('REG_VOLTAGE_D',0x21,['f'],[])
    REG_CURRENT_Q = Register('REG_CURRENT_Q',0x22,['f'],[])
    REG_CURRENT_D = Register('REG_CURRENT_D',0x23,['f'],[])
    REG_CURRENT_A = Register('REG_CURRENT_A',0x24,['f'],[])
    REG_CURRENT_B = Register('REG_CURRENT_B',0x25,['f'],[])
    REG_CURRENT_C = Register('REG_CURRENT_C',0x26,['f'],[])
    REG_CURRENT_ABC = Register('REG_CURRENT_ABC',0x27,['f','f','f'],[])
    REG_CURRENT_DC = Register('REG_CURRENT_DC',0x28,['f','f'],[])

    REG_VEL_PID_P = Register('REG_VEL_PID_P',0x30,['f'],['f'])
    REG_VEL_PID_I = Register('REG_VEL_PID_I',0x31,['f'],['f'])
    REG_VEL_PID_D = Register('REG_VEL_PID_D',0x32,['f'],['f'])
    REG_VEL_LPF_T = Register('REG_VEL_LPF_T',0x33,['f'],['f'])
    REG_ANG_PID_P = Register('REG_ANG_PID_P',0x34,['f'],['f'])
    REG_VEL_LIMIT = Register('REG_VEL_LIMIT',0x35,['f'],['f'])
    REG_VEL_MAX_RAMP = Register('REG_VEL_MAX_RAMP',0x36,['f'],['f'])

    REG_CURQ_PID_P = Register('REG_CURQ_PID_P',0x40,['f'],['f'])
    REG_CURQ_PID_I = Register('REG_CURQ_PID_I',0x41,['f'],['f'])
    REG_CURQ_PID_D = Register('REG_CURQ_PID_D',0x42,['f'],['f'])
    REG_CURQ_LPF_T = Register('REG_CURQ_LPF_T',0x43,['f'],['f'])
    REG_CURD_PID_P = Register('REG_CURD_PID_P',0x44,['f'],['f'])
    REG_CURD_PID_I = Register('REG_CURD_PID_I',0x45,['f'],['f'])
    REG_CURD_PID_D = Register('REG_CURD_PID_D',0x46,['f'],['f'])
    REG_CURD_LPF_T = Register('REG_CURD_LPF_T',0x47,['f'],['f'])

    REG_VOLTAGE_LIMIT = Register('REG_VOLTAGE_LIMIT',0x50,['f'],['f'])
    REG_CURRENT_LIMIT = Register('REG_CURRENT_LIMIT',0x51,['f'],['f'])
    REG_MOTION_DOWNSAMPLE = Register('REG_MOTION_DOWNSAMPLE',0x52,['i'],['i'])
    REG_DRIVER_VOLTAGE_LIMIT = Register('REG_DRIVER_VOLTAGE_LIMIT',0x53,['f'],['f'])
    REG_PWM_FREQUENCY = Register('REG_PWM_FREQUENCY',0x54,['i'],['i'])
    REG_VOLTAGE_SENSOR_ALIGN = Register('REG_VOLTAGE_SENSOR_ALIGN',0x55,['f'],['f'])

    REG_ZERO_ELECTRIC_ANGLE = Register('REG_ZERO_ELECTRIC_ANGLE',0x60,['f'],['f'])
    REG_SENSOR_DIRECTION = Register('REG_SENSOR_DIRECTION',0x61,['b'],['b'])
    REG_ZERO_OFFSET = Register('REG_ZERO_OFFSET',0x62,['f'],['f'])
    REG_POLE_PAIRS = Register('REG_POLE_PAIRS',0x63,['b'],['b'])
    REG_PHASE_RESISTANCE = Register('REG_PHASE_RESISTANCE',0x64,['f'],['f'])
    REG_KV = Register('REG_KV',0x65,['f'],['f'])
    REG_INDUCTANCE = Register('REG_INDUCTANCE',0x66,['f'],['f'])

    REG_NUM_MOTORS = Register('REG_NUM_MOTORS',0x70,['b'],['b'])
    REG_SYS_TIME = Register('REG_SYS_TIME',0x71,['i'],[])



def parse_register(regstr:str|int):
    """ Parse a register string or int to a Register object """
    if isinstance(regstr, Register):
        return regstr
    if isinstance(regstr, int):
        return SimpleFOCRegisters.by_id(regstr)
    if regstr.startswith('0x'):
        return SimpleFOCRegisters.by_id(int(regstr, 16))
    if regstr.isdigit():
        return SimpleFOCRegisters.by_id(int(regstr))
    if regstr.startswith('REG_'):
        return SimpleFOCRegisters.__getattribute__(SimpleFOCRegisters, regstr.upper())
    return SimpleFOCRegisters.__getattribute__(SimpleFOCRegisters, "REG_"+regstr.upper())

        
