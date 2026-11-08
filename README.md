# CE4IB: Building Energy Simulation

**Author:** Lino Kaiser.

Thermal modelling and simulation of the Winterthur campus-inspired
teaching pavilion: one storey, 54 m², a 36 m² student project room and an 18 m² office.
The geometry and construction are chosen model assumptions, inspired by ZHAW
Campus Technikumstrasse.

## Project files

- [Assignment 1: Model](01_model.ipynb): geometry, materials, occupancy, boundary
  conditions, numbered circuit, conductances, capacities and DAE matrices.
- [Assignment 2: Steady-state](02_steady_state.ipynb): DAE/state-space comparison
  and independent heat-balance checks.
- [Assignment 3: Simulate step response](03_simulate_step_response.ipynb):
  time-step selection, settling times and step responses.
- [Assignment 4: Simulate response to weather](04_simulate_response_to_weather.ipynb):
  Zurich Airport weather, solar and internal gains, heating controllers and window shading.
- [Shared weather and simulation helpers](simulation.py), used by notebook 4.
- [Shared thermal circuit](thermal_model.py), used by the model and simulation notebooks.
- [Building parameters](building.py), shared by notebooks.
- [Floor plan](figures/building_layout.svg) and [thermal circuit](figures/thermal_circuit.svg).
- [Notebook environment](environment.yml).

## Run

[Open in Binder](https://mybinder.org/v2/gh/linokaiser/CE4IB/main?urlpath=%2Fdoc%2Ftree%2F01_model.ipynb)

The notebooks use NumPy, pandas, Matplotlib and SciPy. The selected Zurich Airport
TMYx 2009–2023 EPW file is included in `weather_data`.
