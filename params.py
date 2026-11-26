# This file will contain all parameters used in this project which are not calculated inside code,
# but have been defined bevorhand, and are needed for the calculations that follow


brick = {
    "cond": 0.8,
    "density": 1800
}

concrete = {
    "cond": 2.0,
    "density": 2400
}

external_wall = {

    "thickness": 0.35,
    "area": 39.9, # (54.0 - 2.1 - 8 - 4)
    "volume": 39.9 * 0.35

}

internal_wall = {

    "thickness": 0.25,
    "area": 15.9, # (18.0 - 2.1)
    "volume": 15.9 * 0.25
}

roof = {

    "thickness": 0.35,
    "area": 54.0,
    "volume": 54.0 * 0.35
}

floor = {

    "thickness": 0.25,
    "area": 54.0,
    "volume": 54.0 * 0.25
}

door = {

    "thickness": 0.04,
    "area": 2.1,
    "u": 2.0
}

student_window = {
    "area": 8,
    "u": 2.0
}

office_window = {
    "area": 4,
    "u": 2.0
}

hc = 3
hr = 5
air_density = 1.2
specific_heat_capacity = 1005
air_change_rate = 1
student_volume = 108
office_volume = 54
heat_capacity = 1000
