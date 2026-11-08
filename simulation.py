"""Weather preparation and explicit Euler integration."""

import numpy as np
import pandas as pd

import dm4bem
import thermal_model as model

boundary = model.boundary
state_nodes = np.flatnonzero(model.capacities)
air_states = np.flatnonzero(np.isin(state_nodes, model.air_nodes))
floor_mass_nodes = [5, 12]
flow_mask = model.f.copy()
flow_mask[floor_mass_nodes] = 1
flow_nodes = np.flatnonzero(flow_mask)
source_branches = np.flatnonzero(model.b)
input_names = (
    [f"b_T[{j}] [°C]: {model.branches[j][1]}" for j in source_branches]
    + [f"f_Q[{j}] [W]: {model.node_names[j]}" for j in flow_nodes]
)
weather_matrices = [
    model.state_space(ach=boundary[key], flow_mask=flow_mask)
    for key in ["unoccupied_ACH", "occupied_ACH"]
]
occupied_gains = np.array([
    model.zones[name]["people"] * boundary["person_sensible_W"]
    + model.zones[name]["laptops"] * boundary["laptop_W"]
    + model.areas[name]["floor"] * boundary["lighting_W_m2"]
    for name in model.zone_names
])


def solar_inputs(weather, meta):
    """Calculate facade irradiance, sol-air offsets and transmitted window heat."""
    # The helper adds 60 min internally. Shift its index to evaluate the midpoint
    # of each EPW hour in approximate local solar time.
    midpoint = weather.index + pd.Timedelta(minutes=30)
    B = 2 * np.pi * (midpoint.dayofyear.to_numpy() - 81) / 364
    equation_of_time = 9.87 * np.sin(2 * B) - 7.53 * np.cos(B) - 1.5 * np.sin(B)
    solar_correction = 4 * (meta["longitude"] - 15 * meta["TZ"]) + equation_of_time
    solar_weather = weather.copy()
    solar_weather.index = midpoint + pd.to_timedelta(solar_correction - 60, unit="min")
    irradiance = pd.DataFrame(index=weather.index)
    for orientation, azimuth in {"south": 0, "west": 90, "north": 180, "east": -90}.items():
        surface = {"slope": 90, "azimuth": azimuth, "latitude": meta["latitude"]}
        radiation = dm4bem.sol_rad_tilt_surf(
            solar_weather, surface, boundary["ground_reflectance"])
        reflected = weather["ghi"].to_numpy() * boundary["ground_reflectance"] / 2
        irradiance[orientation] = (radiation["direct"].to_numpy()
                                  + radiation["diffuse"].to_numpy() + reflected)
    irradiance["roof"] = weather["ghi"]
    assert np.isfinite(irradiance.to_numpy()).all()
    assert (irradiance >= -1e-8).all().all()

    hourly = weather[["temp_air"]].join(irradiance)
    solar_rows = []
    for name in model.zone_names:
        zone = model.zones[name]
        side = "west" if name == "project_room" else "east"
        facade_areas = {
            "north": zone["width_m"] * zone["height_m"],
            "south": zone["width_m"] * zone["height_m"],
            side: zone["depth_m"] * zone["height_m"],
        }
        window_gain = np.zeros(len(hourly))
        for opening in model.openings:
            if opening["zone"] != name:
                continue
            area = opening["width_m"] * opening["height_m"]
            facade_areas[opening["orientation"]] -= area
            if opening["kind"] == "window":
                window_gain += (area * boundary["glazing_fraction"] * boundary["glazing_g"]
                                * irradiance[opening["orientation"]].to_numpy())
        wall_area = sum(facade_areas.values())
        assert np.isclose(wall_area, model.areas[name]["external_wall"])
        mean_wall_irradiance = sum(area * irradiance[side] for side, area in facade_areas.items()) / wall_area
        hourly[name + "_wall_solair"] = boundary["wall_solar_absorptance"] * model.r_outside * mean_wall_irradiance
        hourly[name + "_window_gain"] = window_gain
        solar_rows.append({"Zone": name, **facade_areas,
                           "Annual window gain [kWh]": window_gain.sum() / 1000})
    hourly["roof_solair"] = boundary["roof_solar_absorptance"] * model.r_outside * irradiance["roof"]
    return hourly, pd.DataFrame(solar_rows).set_index("Zone")


def sampled_weather(hourly, start, stop, step, warmup_days=60):
    """Resample weather and add the existing Zurich occupancy and setpoints."""
    previous_year = hourly.copy()
    previous_year.index = previous_year.index.map(lambda t: t.replace(year=2022))
    extended_weather = pd.concat([previous_year, hourly])
    start = pd.Timestamp(start, tz=hourly.index.tz)
    stop = pd.Timestamp(stop, tz=hourly.index.tz)
    begin = start - pd.Timedelta(days=warmup_days)
    index = pd.date_range(begin, stop, freq=pd.to_timedelta(step, unit="s"))
    sample = extended_weather.reindex(index, method="ffill")
    sample["temp_air"] = extended_weather["temp_air"].reindex(index).interpolate(method="time")
    civil_time = index.tz_convert("Europe/Zurich")
    occupied = (np.isin(civil_time.dayofweek, boundary["occupied_weekdays"])
                & (civil_time.hour >= boundary["occupied_hours_local"][0])
                & (civil_time.hour < boundary["occupied_hours_local"][1]))
    sample["occupied"] = occupied
    sample["setpoint"] = np.where(occupied, boundary["occupied_setpoint_C"],
                                  boundary["unoccupied_setpoint_C"])
    assert sample.notna().all().all()
    return sample


def input_values(sample, solar=True, internal=True, window_factor=1.0):
    """Pack temperature sources and heat gains; controller heat is added separately."""
    n = len(sample)
    inputs = np.zeros((n, len(source_branches) + len(flow_nodes)))
    outdoor = sample["temp_air"].to_numpy()
    for col, branch in enumerate(source_branches):
        path, source, _, _ = model.branches[branch]
        if source == "ground":
            inputs[:, col] = boundary["ground_temperature_C"]
        elif source == "setpoint":
            inputs[:, col] = sample["setpoint"]
        else:
            inputs[:, col] = outdoor
            if solar and "external_wall outside" in path:
                name = path.split(":")[0]
                inputs[:, col] += sample[name + "_wall_solair"]
            elif solar and "roof outside" in path:
                inputs[:, col] += sample["roof_solair"]
    for j, name in enumerate(model.zone_names):
        air_col = len(source_branches) + np.flatnonzero(flow_nodes == model.air_nodes[j])[0]
        floor_col = len(source_branches) + np.flatnonzero(flow_nodes == floor_mass_nodes[j])[0]
        inputs[:, air_col] = internal * occupied_gains[j] * sample["occupied"].to_numpy()
        inputs[:, floor_col] = solar * window_factor * sample[name + "_window_gain"].to_numpy()
    return inputs


def simulation_matrices(sample, step, solar=True, internal=True, window_factor=1.0):
    """Return Euler state matrices and weather/internal forcing at both ACH rates."""
    inputs = input_values(sample, solar, internal, window_factor)
    Ad = [np.eye(len(As)) + step * As for As, _, _, _ in weather_matrices]
    forcing = [step * (inputs[:-1] @ Bs.T) for _, Bs, _, _ in weather_matrices]
    return Ad, forcing


def simulate_weather(sample, step, solar=True, internal=True, heating=False,
                     initial=20.0, max_power=None, return_state=False, kp=500.0):
    """Run the proportional controller; optionally return its final storage state."""
    Ad, forcing = simulation_matrices(sample, step, solar, internal)
    mode = sample["occupied"].to_numpy(dtype=int)
    setpoint = sample["setpoint"].to_numpy()
    state = np.full(len(state_nodes), initial, dtype=float)
    temperature = np.empty((len(sample), 2))
    heat = np.zeros((len(sample), 2))
    temperature[0] = state[air_states]
    air_capacity = model.capacities[model.air_nodes]
    for k in range(len(sample) - 1):
        if heating:
            heat[k] = np.maximum(kp * (setpoint[k] - state[air_states]), 0)
            if max_power is not None:
                heat[k] = np.minimum(heat[k], max_power)
        state = Ad[mode[k]] @ state + forcing[mode[k]][k]
        state[air_states] += step * heat[k] / air_capacity
        temperature[k + 1] = state[air_states]
    if heating:
        heat[-1] = np.maximum(kp * (setpoint[-1] - state[air_states]), 0)
        if max_power is not None:
            heat[-1] = np.minimum(heat[-1], max_power)
    assert np.isfinite(temperature).all() and np.isfinite(heat).all()
    assert (heat >= 0).all()
    result = pd.DataFrame({
        "Project [°C]": temperature[:, 0], "Office [°C]": temperature[:, 1],
        "Project heating [W]": heat[:, 0], "Office heating [W]": heat[:, 1],
        "Setpoint [°C]": setpoint, "Occupied": mode.astype(bool),
    }, index=sample.index)
    return (result, state.copy()) if return_state else result
