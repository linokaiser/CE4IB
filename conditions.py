# This file contains all the parameters used in this project that are defined beforehand
# and are needed for the calculations that follow.

import numpy as np


brick = {
    "conduction": 0.8,  # W/(m·K)
    "density": 1800  # kg/m³
}

concrete = {
    "conduction": 2.0,  # W/(m·K)
    "density": 2400  # kg/m³
}

external_wall = {
    "thickness": 0.35,  # m
    "student_area": 43.9,  # m², calculated as 54.0 - 8.0 - 2.1
    "office_area": 32.0  # m², calculated as 36.0 - 4.0
}

internal_wall = {
    "thickness": 0.25,  # m
    "area": 15.9  # m², calculated as 18.0 - 2.1
}

roof = {
    "thickness": 0.35,  # m
    "student_area": 36.0,  # m²
    "office_area": 18.0  # m²
}

floor = {
    "thickness": 0.25,  # m
    "student_area": 36.0,  # m²
    "office_area": 18.0  # m²
}

door = {
    "thickness": 0.04,  # m
    "area": 2.1,  # m²
    "u": 2.0  # W/(m²·K)
}

student_window = {
    "area": 8,  # m²
    "u": 2.0  # W/(m²·K)
}

office_window = {
    "area": 4,  # m²
    "u": 2.0  # W/(m²·K)
}

hc = 3  # W/(m²·K)
hr = 5  # W/(m²·K)
air_density = 1.2  # kg/m³
air_change_rate = 1  # h⁻¹
student_volume = 108  # m³
office_volume = 54  # m³
heat_capacity = 1000  # J/(kg·K)

time_step_duration = 60  # s

outside_temperature = 0  # °C
floor_temperature = 10  # °C
student_heat_gain = 600 + 0 # W (internal gains + any heating you would want to add using a heater or something similar)
office_heat_gain = 400  + 0 # W(internal gains + any heating you would want to add using a heater or something similar)

# Incidence matrix derived by hand in OneNote.
A = np.array([
    [ 0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0, -1,  1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0, -1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0, -1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1,  1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1,  1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0],
    [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0, -1],
    [-1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0],
])

# Temperature inputs in °C
u = np.array([outside_temperature, outside_temperature, floor_temperature, outside_temperature, outside_temperature, outside_temperature, outside_temperature, outside_temperature, floor_temperature, outside_temperature, outside_temperature, student_heat_gain, office_heat_gain,])