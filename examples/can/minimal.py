#!/usr/bin/env python3
"""Minimal CAN example for SimpleFOC"""

import simplefoc.packets as packets
from simplefoc import motors
import time

# Connect to CAN
motors = motors.can('can0', target_address=0x01, bitrate=1000000)
motors.connect()

# Get motor
motor = motors.motor(0)

# Control
motor.enable()
motor.set_target(2.0)

angle = motor.get_angle()    
print(f"Angle: {angle}")

velocity = motor.get_velocity()
print(f"Velocity: {velocity}")

torque_mode = motor.get_torque_mode()
print(f"Torque Control: {torque_mode}")
motion_mode = motor.get_motion_control_type()
print(f"Motion Control: {motion_mode}")

velocity_pid_params = motor.get_velocity_pid()
print(f"Velocity PID params: {velocity_pid_params}")

time.sleep(1)

print("Setting Angle PID to P:10.0, I:2.0, D:0.01")
motor.set_angle_pid(10.0, 2.0, 0.01)

time.sleep(1)
angle_pid_params = motor.get_angle_pid()
print(f"Angle PID params: {angle_pid_params}")

time.sleep(1)
motor_params = motor.get_motor_parameters()
print(f"Motor parameters: {motor_params}")

# Cleanup
motors.disconnect()
