from params import *
import numpy as np

# Define simple conuction formula next as a function so it can be reused

def conduction(cond, area, thickness):
    
    return cond * area / thickness


# Next lets define all the conductances, and let python calculate the values. I will start with the wall as proof of concept

G0 = conduction(brick["cond"], external_wall["area"], (external_wall["thickness"] / 2 ))
G1 = G15 = G16 = G0

G4 = conduction(concrete["cond"], roof["area"], (roof["thickness"] / 2 ))
G5 = G19 = G20 = G4

G8 = conduction(brick["cond"], floor["area"], (floor["thickness"] / 2 ))
G9 = G23 = G24 = G8

# It works, therfore we can now start extending the approach that was taken. In doing so i will use the following obious observations:

# G0, G1 G 15 and G16 are the same.

# G4 G5, G19 and G20 are the same

# G3 G3 G9 G23 and G24 are the same.

# The only difference is that one is wall, one is roof and one is floor, therfore it would make sense to put them into the params. However did we define it all? lets check 

# it still runs, and looks good to me, so next lets do the convection and radiation for this we will need hr and hc
# which we have not defined yet, so lets go do that now :)


def convection (hc, area):
    return hc * area

def radiation (hr, area):
    return hr * area

G2 = convection(hc, external_wall["area"])
G17 = G2

G6 = convection(hc, roof["area"])
G21 = G6

G10 = convection(hc, floor["area"])
G25 = G10



G3 = radiation(hr, external_wall["area"])
G18 = G3

G7 = radiation(hr, roof["area"])
G22 = G7

G11 = radiation(hr, floor["area"])
G26 = G11

# Okay that leaves me with window, doors, ventilation and internal wall. For the internal wall no brainer we can reuse same approach as for external
# 

G29 = conduction(brick["cond"], internal_wall["area"], (internal_wall["thickness"] / 2 ))
G30 = G29

# That means only window door and ventilation are left
G13 = door["u"] * door["area"]
G31 = G13

G12 = student_window["u"] * student_window["area"]
G27 = office_window["u"] * office_window["area"]

#That leaves ventilation
# according to my research the formula for ventilation conductance is

# air density * Specific heat capacity * ((air change rate * volume)/3600)
G14 = air_density * specific_heat_capacity * ((air_change_rate * student_volume)/3600)
G28 = air_density * specific_heat_capacity * ((air_change_rate * office_volume)/3600)


# Ventilation conductance
# Source: supplied notebook 03CubicBuilding.ipynb, section "Advection".
#
# G_v   = rho_air * c_air * V_dot           [W/K]
# V_dot = ACH * V_air / 3600               [m^3/s]
#
# Combined:
# G_v = rho_air * c_air * ACH * V_air / 3600
#
# rho_air: air density                     [kg/m^3]
# c_air:   specific heat capacity of air   [J/(kg K)]
# V_air:   air volume in the room          [m^3]
# ACH:     air changes per hour            [1/h]
#
# The factor 3600 converts hours to seconds.
# The material calls this "conductance of advection by ventilation
# and/or infiltration".





# for i in range(0, 32):
#     print(f"G{i} = {eval(f'G{i}')}")

# So far so good, next the capacities, which are easier, because there are only 8.

# Okay so according to the provided sources the capacities is calculated by using density, heat capacity, and volume

C0 = air_density * specific_heat_capacity * student_volume
C1 = brick["density"] * specific_heat_capacity * external_wall["volume"]
C5 = C1
C2 = concrete["density"] * specific_heat_capacity * roof["volume"]
C6 = C2
C3 = concrete["density"] * specific_heat_capacity * floor["volume"]
C7 = C3
C8 = brick["density"] * specific_heat_capacity * internal_wall["volume"]
C4 = air_density * specific_heat_capacity * office_volume


# for i in range(0, 9):
#     print(f"C{i} = {eval(f'C{i}')}")




# it works, so lets see whats next


#  - Write down the incidence matrix $A$, the conductance matrix $G$ and the capacity matrix $C$ of the system of Algebraic Differential Equations (DAE).

# Which is probably best/easier to put it into notebook 1.

# Our next task is to put the matrixes and vectors we have into python.

# For most of them this is rather easy and straight forward, so lets start with them.

G = np.diag([G0, G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14, G15, G16, G17, G18, G19, G20, G21, G22, G23, G24, G25, G26, G27, G28, G29, G30, G31])
#Future note for self, this can be refactored to use G{i}

# Isnt autofill great, welcome to the future

C = np.diag([C0, C1, 0, C2, 0, C3, 0, C4, C5, 0, C6, 0, C7, 0, C8])

# lets do matrix a next which for now as its late i dont even care about a elegant solution, i will just type out what i derived manually

# A = np.zeros((32, 15))

# print("a = ", A)

# A[1,1] = -1
# A[1,1] = -1

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

# note, refactor as i know its easaily possible to make a 0 matrix and fill in values, but is it better tho? 


# Next lets do the vectors. For reason of code beauty i like to use row verctors and transpose them so the become colum vectors




T1 = T3 = T4 = T5 = T6 = T7 = T9 = T10 = T0 = 0
T8 = T2 = 10

b = np.array([
    1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0
])

f = np.array([
    1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0
])

# With that we have succesfully finished notbook one. Refactoring will be done later one, by me by hand

# To convert to state space we can use the code provided in the github of the proffesor.

# According to that we also need a indication vector y

#         y : TYPE np.array
#             vector indicating the temperatures in the outputs:
#                 1 for output nodes, otherwise 0

# In my case the output nodes i am interessted in of course are zero and 7.

# therfor:


y = np.array([1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0])

# Okay, lets import and use the code

import dm4bem

        # Returns
        # -------
        # As state matrix in state equation
        # Bs input matrix in state equation
        # Cs output matrix in observation equation
        # Ds input matrix in observation equation
        # Idx{1} nodes with capacities
        #     {2} branches with temp. sources
        #     {3} nodes with flow sources
        #     {4} nodes output temperatures

As, Bs, Cs, Ds = dm4bem.tc2ss(A, G, C, b, f, y)

# Lets print them to make sure it works

# print("As = ", As)
# print("Bs = ", Bs)
# print("Cs = ", Cs)
# print("Ds = ", Ds)


# next we have the task of solving the steady state.

# Like defined lets use two: 

# we start with 0 degree outside and 10 degree floor:

u = np.array([0, 0, 10, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0])



# If we wanted 20 degrees outside, just comment in our out as one pleases:
# u = np.array([20, 20, 10, 20, 20, 20, 20, 20, 10, 20, 20, 20, 20])


storage_temps = -np.linalg.solve(As, Bs @ u)
air_temps = Cs @ storage_temps + Ds @ u

print("y_ss = ", air_temps)


# this follows from

# Steady-state calculation from the state-space model
# Source: supplied notebook dm4bem/03CubicBuilding.ipynb, sections:
# - "State-space representation"
# - "Steady-state from state-space representation"
#
# yss = (-Cs @ np.linalg.inv(As) @ Bs + Ds) @ u
# print(f'yss = {yss} °C')


b_values = np.zeros(32)
b_values[8] = 10    
b_values[23] = 10   

f_values = np.zeros(15)

temperatures_of_nodes = np.linalg.solve(
    A.T @ G @ A,
    A.T @ G @ b_values + f_values

)

print(temperatures_of_nodes[[0, 7]])  


# Steady-state calculation directly from the DAE
# Source: supplied notebook dm4bem/03CubicBuilding.ipynb, sections:
# - "System of algebraic-differential equations (DAE)"
# - "Steady-state from differential algebraic equations (DAE)"
# θ = np.linalg.inv(A.T @ G @ A) @ (A.T @ G @ b + f)
# print(f'θ = {θ} °C')



#Step 1: calculate the eigenvalues of As:

eigenvalues = np.linalg.eigvals(As)

print("eigenvalues = ", eigenvalues)

#Step 2: we need to convert them into time constants

tc = -1 / eigenvalues

print ("ti =", tc)

#Step 3: We know delta t has be to smaller than 2 * the smallest time constant
tc_min = np.min (tc)

print ("tc_min =", tc_min)

# Now we can get delta t 

delta_t = 2 * tc_min

print ("delta_t =", delta_t)

# Lastly according to the supplied sources settling time:
# t_settle = 4 * max(-1 / λ)
# print(f'Settling time: {t_settle:.2f} s = {t_settle / 3600:.2f} h')
# So lets just reuse that code:


settling_time = 4 * max(-1 / eigenvalues)
print ("settling_time =", settling_time)

# So the answer to the first task is as follows

# The maximum allowed timestep for explicit euler is 187.49 seconds, but i will be using 60 seconds, and settling time is around 4.85 days

# the provided sources integrate as follows:


# # Step response
# # -------------
# # duration: next multiple of 3600 s that is larger than t_settle
# duration = np.ceil(t_settle / 3600) * 3600
# n = int(np.floor(duration / dt))    # number of time steps
# t = np.arange(0, n * dt, dt)        # time vector for n time steps

# print(f'Duration = {duration} s')
# print(f'Number of time steps = {n}')
# # pd.DataFrame(t, columns=['time'])

# # initial conditions
# n_s = As.shape[0]                      # number of state variables
# θ_exp = np.zeros([n_s, t.shape[0]])    # explicit Euler in time t
# θ_imp = np.zeros([n_s, t.shape[0]])    # implicit Euler in time t

# # time integration
# I = np.eye(n_s)                        # identity matrix

# for k in range(n - 1):
#     θ_exp[:, k + 1] = (I + dt * As) @ θ_exp[:, k]\
#         + dt * Bs @ u[k, :]
#     θ_imp[:, k + 1] = np.linalg.inv(I - dt * As) @ (θ_imp[:, k]\
#         + dt * Bs @ u[k, :])   

# # outputs
# y_exp = Cs @ θ_exp + Ds @  u.T
# y_imp = Cs @ θ_imp + Ds @  u.T





# So again i will be reusing that Code

duration = np.ceil(settling_time / 3600) * 3600
time_step = 60
n = int(np.floor(duration / time_step))
t = np.arange(0, n * time_step, time_step)

u = np.tile(u, (n, 1))

print(f'Duration = {duration} s')
print(f'Number of time steps = {n}')


n_s = As.shape[0]                     
θ_exp = np.zeros([n_s, t.shape[0]])    

# time integration
I = np.eye(n_s)                        # identity matrix

for k in range(n - 1):
    θ_exp[:, k + 1] = (I + time_step * As) @ θ_exp[:, k]\
        + time_step * Bs @ u[k, :] 

y_exp = Cs @ θ_exp + Ds @  u.T

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(t / 86400, y_exp.T)
ax.set(xlabel='Time in days',
       ylabel='Temperature in °C',
       title='Step response indoor temperature')
ax.legend(["Project room", "Office"])
ax.grid()
plt.show()