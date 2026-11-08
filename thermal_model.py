"""Thermal circuit shared by the steady-state and dynamic notebooks."""

import numpy as np

import dm4bem
from building import definition

building = definition["building"]
zones = definition["zones"]
openings = definition["openings"]
materials = definition["materials"]
assemblies = definition["assemblies"]
boundary = definition["boundary"]

zone_names = ["project_room", "office"]
air_nodes = [0, 7]
rho_air = 1.2       # kg/m³, assumed
cp_air = 1005       # J/(kg K), assumed
r_inside = boundary["inside_combined_film_R_m2K_W"]
r_outside = boundary["outside_combined_film_R_m2K_W"]
h_convection = 3.0
h_radiation = 1 / r_inside - h_convection

areas = {}
for name in zone_names:
    zone = zones[name]
    own_openings = [o for o in openings if o["zone"] == name]
    windows = sum(o["width_m"] * o["height_m"] for o in own_openings
                  if o["kind"] == "window")
    doors = sum(o["width_m"] * o["height_m"] for o in own_openings
                if o["kind"] == "external_door")
    floor = zone["width_m"] * zone["depth_m"]
    gross_walls = (2 * zone["width_m"] + zone["depth_m"]) * zone["height_m"]
    areas[name] = {
        "external_wall": gross_walls - windows - doors,
        "roof": floor,
        "floor": floor,
        "windows": windows,
        "external_door": doors,
        "volume": floor * zone["height_m"],
    }

internal_door = next(o for o in openings if o["kind"] == "internal_door")
door_area = internal_door["width_m"] * internal_door["height_m"]
partition_area = building["reference_depth_m"] * building["height_m"] - door_area


def element_properties(assembly, area):
    # The main masonry/concrete layer is at position 1 in each assembly.
    resistance = [d / materials[m]["lambda_W_mK"] for m, d in assemblies[assembly]]
    r_inner = resistance[0] + resistance[1] / 2
    r_outer = resistance[1] / 2 + sum(resistance[2:])
    capacity = area * sum(
        d * materials[m]["rho_kg_m3"] * materials[m]["cp_J_kgK"]
        for m, d in assemblies[assembly]
    )
    return r_inner, r_outer, capacity

node_names = [
    "Project air", "Project wall mass", "Project wall surface",
    "Project roof mass", "Project roof surface",
    "Project floor mass", "Project floor surface",
    "Office air", "Office wall mass", "Office wall surface",
    "Office roof mass", "Office roof surface",
    "Office floor mass", "Office floor surface", "Shared partition",
]
capacities = np.zeros(len(node_names))
branches = []       # Each row: name, start node/source, end node, conductance
ventilation_branches = []
heating_branches = []

for zone_index, name in enumerate(zone_names):
    offset = 7 * zone_index
    air = offset
    capacities[air] = rho_air * cp_air * areas[name]["volume"]

    for element, mass, surface in [
        ("external_wall", offset + 1, offset + 2),
        ("roof", offset + 3, offset + 4),
        ("floor", offset + 5, offset + 6),
    ]:
        area = areas[name][element]
        r_inner, r_outer, capacities[mass] = element_properties(element, area)
        source = "ground" if element == "floor" else "outdoor"
        exterior_film = 0 if element == "floor" else r_outside
        branches.extend([
            (f"{name}: {element} outside", source, mass,
             area / (r_outer + exterior_film)),
            (f"{name}: {element} inside", mass, surface, area / r_inner),
            (f"{name}: {element} convection", surface, air, h_convection * area),
            (f"{name}: {element} radiation", surface, air, h_radiation * area),
        ])

    branches.append((f"{name}: windows", "outdoor", air,
                     boundary["window_U_W_m2K"] * areas[name]["windows"]))
    if areas[name]["external_door"] > 0:
        branches.append((f"{name}: exterior door", "outdoor", air,
                         boundary["external_door_U_W_m2K"]
                         * areas[name]["external_door"]))
    ventilation_branches.append(len(branches))
    branches.append((f"{name}: ventilation", "outdoor", air,
                     rho_air * cp_air * areas[name]["volume"] / 3600))
    heating_branches.append(len(branches))
    branches.append((f"{name}: P-controller", "setpoint", air, 0.0))

r_left, r_right, capacities[14] = element_properties("partition", partition_area)
partition_branches = [len(branches), len(branches) + 1]
branches.extend([
    ("Partition: project side", 0, 14, partition_area / (r_inside + r_left)),
    ("Partition: office side", 14, 7, partition_area / (r_right + r_inside)),
])
door_resistance = sum(d / materials[m]["lambda_W_mK"]
                      for m, d in assemblies["internal_door"])
internal_door_branch = len(branches)
branches.append(("Internal door", 0, 7, door_area / (2 * r_inside + door_resistance)))

n_branches = len(branches)
n_nodes = len(node_names)
A = np.zeros((n_branches, n_nodes))
base_conductance = np.array([row[3] for row in branches])
b = np.zeros(n_branches, dtype=int)

for j, (_, start, end, _) in enumerate(branches):
    A[j, end] = 1
    if isinstance(start, str):
        b[j] = 1
    else:
        A[j, start] = -1

G = np.diag(base_conductance)       # 1 ACH, no heating controller
C = np.diag(capacities)
f = np.zeros(n_nodes, dtype=int)
f[air_nodes] = 1
y = np.zeros(n_nodes, dtype=int)
y[air_nodes] = 1


def state_space(ach=1.0, kp=0.0, flow_mask=None):
    """Return the circuit state-space matrices for one operating condition."""
    conductance = base_conductance.copy()
    conductance[ventilation_branches] *= ach
    conductance[heating_branches] = kp
    source_mask = f if flow_mask is None else flow_mask
    return dm4bem.tc2ss(A, np.diag(conductance), C, b, source_mask, y)
