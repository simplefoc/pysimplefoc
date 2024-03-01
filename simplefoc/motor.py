
from .registers import SimpleFOCRegisters
from rx import operators as ops

class Motor:
    """ SimpleFOC Motor class
        Abstracts a single motor, and provides a high-level interface to control and query it.

        Typically, you will get a Motor instance by calling motors.motor(motor_id)

        @param motors: the Motors instance
        @param motor_id: the motor id
    """
    def __init__(self, motors, motor_id):
        self.motors = motors
        self.motor_id = motor_id
    
    def observable(self):
        return self.motors.observable().pipe(ops.filter(lambda p: p.motor_id == self.motor_id))
    
    def listen(self, listener):
        return self.observable().subscribe(listener)
    
    def set_register(self, reg, values):
        self.motors.set_register(self.motor_id, reg, values)

    def get_register(self, reg, timeout:float=1.0):
        return self.motors.get_register(self.motor_id, reg, timeout)

    def set_target(self, target):
        target = float(target)
        self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_TARGET, target)

    def set_mode(self, motion_control_type, torque_control_type):
        # todo check types
        self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_CONTROL_MODE, motion_control_type.value)
        self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_TORQUE_MODE, torque_control_type.value)

    def set_limits(self, max_voltage:float=None, max_current:float=None, max_velocity:float=None, max_angle:float=None, min_angle:float=None):
        if (max_voltage!=None): self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VOLTAGE_LIMIT, float(max_voltage))
        if (max_current!=None): self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_CURRENT_LIMIT, float(max_current))
        if (max_velocity!=None): self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VELOCITY_LIMIT, float(max_velocity))
        # todo add max and min angle limits to SimpleFOC
        #self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANGLE_LIMIT_H, float(max_angle))
        #self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANGLE_LIMIT_L, float(min_angle))

    # todo change PID registers to give/take 6 values
    def set_velocity_pid(self, p:float = None, i:float = None, d:float = None, limit:float = None, ramp:float = None, tf:float = None):
        if p != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VEL_PID_P, float(p))
        if i != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VEL_PID_I, float(i))
        if d != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VEL_PID_D, float(d))
        if limit != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VEL_PID_LIM, float(limit)) # todo this is not exactly correct
        if ramp != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VEL_PID_RAMP, float(ramp))
        if tf != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_VEL_LPF_T, float(tf))

    def set_angle_pid(self, p:float = None, i:float = None, d:float = None, limit:float = None, ramp:float = None, tf:float = None):
        if p != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANG_PID_P, float(p))
        if i != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANG_PID_I, float(i)) # todo add missing registers
        if d != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANG_PID_D, float(d))
        if limit != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANG_PID_LIM, float(limit))
        if ramp != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANG_PID_RAMP, float(ramp))
        if tf != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ANG_LPF_T, float(tf))

    def set_motor_parameters(self, resistance:float=None, kv:float=None, inductance:float=None, pole_pairs:int=None):
        if kv != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_KV, float(kv))
        if resistance != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_PHASE_RESISTANCE, float(resistance))
        if inductance != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_PHASE_INDUCTANCE, float(inductance))
        if pole_pairs != None: self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_POLE_PAIRS, int(pole_pairs))

    def disable(self):
        self.enable(False)

    def enable(self, enable:bool=True):
        self.motors.set_register(self.motor_id, SimpleFOCRegisters.REG_ENABLE, 1 if enable else 0)

    def get_angle(self, timeout:float=1.0):
        return self.motors.get_register(self.motor_id, SimpleFOCRegisters.REG_ANGLE, timeout)
