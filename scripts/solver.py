from pyomo.environ import *
from pathlib import Path
# import gurobipy
# Output figures
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pyomo.environ import Reals, PositiveReals, NonPositiveReals, NegativeReals, NonNegativeReals, PercentFraction, \
    UnitInterval, Integers, PositiveIntegers, NonPositiveIntegers, NegativeIntegers, NonNegativeIntegers, Binary
# import time
# Data management and treatment
import pandas as pd

path_model_in_set = Path('Data/Input/Sets/')
path_model_in_par = Path('Data/Input/Parameters/')
path_model_out    = Path('Data/Output/')
path_results      = Path('Data/Output/')

m = AbstractModel()

#generadores 1,2,3
m.g = Set()
m.d = Set()
m.p = Set(ordered=True)

#Definición de parámetros

#auxiliary load factor
m.p_k = Param(m.g, within = NonNegativeReals)

#Consumo variable de combustible
m.p_alfa = Param(m.g, within = NonNegativeReals)

#Potencia Máxima del generador
m.p_qmax = Param(m.g, within = NonNegativeReals)

#Potencia Mínima del generador
m.p_qmin = Param(m.g, within = NonNegativeReals)

#Demanda del sistema
m.p_d = Param(m.p,within = NonNegativeReals)

#Coste del combustible €/MW
m.p_f = Param(m.g, within = NonNegativeReals)

#Coste de arranque
m.p_ca = Param(m.g, within = NonNegativeReals)

#Emisiones
m.p_e = Param(m.g, within = NonNegativeReals)

#Coste emisiones
m.p_ce = Param(m.g, within = NonNegativeReals)

#rampa subida
m.p_rs = Param(m.g, within = NonNegativeReals)

#rampa bajada
m.p_rb = Param(m.g, within = NonNegativeReals)

#Beta
m.p_beta = Param(m.g, within = NonNegativeReals)

#Gamma
m.p_gamma = Param(m.g, within = NonNegativeReals)

#Theta
m.p_theta = Param(m.g, within = NonNegativeReals)

#Rendimiento de bombeo de una hydro
m.p_rend = Param(m.g, within  = NonNegativeReals)

#Inflows en el embalse h durante el periodo p
m.p_i = Param (m.p, m.g, within = NonNegativeReals)

#Agua Inicial en una reserva hydro
m.p_w0 = Param (m.g, within = NonNegativeReals)

#Agua final en una reserva
m.p_wfin = Param(m.g, within = NonNegativeReals)

#Limite max de bombeo
m.p_bmax = Param (m.g, within = NonNegativeReals)

#Max water capacity
m.p_wmax = Param (m.g, within = NonNegativeReals)

#Min water amount
m.p_wmin = Param (m.g, within = NonNegativeReals)

#Reserva Rodante
m.p_rod = Param (m.p, within = NonNegativeReals, mutable = True, default = 0)

#Coste de demanda no servida
m.p_cens = Param (within = NonNegativeReals,initialize=180.0)

#Tipo de generador: thermal o hydro
m.p_type = Param(m.g, within = Any)

#Potencia Solar disponible durante el periodo p
m.p_solar = Param(m.p,within = NonNegativeReals)

#Potencia eólica disponible durante el periodo p
m.p_wind = Param(m.p, within= NonNegativeReals)

#Estado de acoplamiento del generador en instante inicial
m.p_u0 = Param(m.g, within = Binary)

#Cantidad mínima de flujo de agua en hydro h en periodo p
m.p_flu = Param(m.g,m.p, within = NonNegativeReals)
m.p_o = Param(m.g, within = NonNegativeReals)


#Definición de variables

#Variable de arranque de un grupo
m.v_y = Var(m.g, m.p, within=Binary)

#Variable de parada de un grupo
m.v_z = Var(m.g,m.p, within=Binary)

#Variable de unit commitment
m.v_u = Var(m.g, m.p, within=Binary)

#Potencia generada por grupo en un periodo
m.v_q = Var(m.g, m.p, within=NonNegativeReals)

#Exceso de potencia generada sobre minimo tecnico
m.v_deltaq = Var(m.g, m.p,within=NonNegativeReals)

#Energy stored in water
m.v_w = Var(m.g, m.p, within = NonNegativeReals)

#Spills de una reserva hydro
m.v_s = Var(m.g, m.p, within = NonNegativeReals)

#Bombeo en una reserva hydro
m.v_b = Var(m.g, m.p, within = NonNegativeReals)

#Cantidad de potencia solar utilizada en el periodo p
m.v_solar = Var(m.p, within = NonNegativeReals)

#Cantidad de potencia eólica utilizada en el periodo p
m.v_wind = Var(m.p, within = NonNegativeReals)

#Potencia no servida
m.v_pns = Var(m.p, within = NonNegativeReals)

# %% Declaration of dynamic sets
def setdin_thermal_generators(m, g):
    return m.p_type[g] == 'thermal'
m.t = Set(ordered=True, initialize=m.g, filter=setdin_thermal_generators, doc="Thermal generators")


def setdin_hydro_generators(m, g):
    return m.p_type[g] == 'hydro'
m.h = Set(ordered=True, initialize=m.g, filter=setdin_hydro_generators, doc="Hydro generators")


#Definición de función objetivo

def e_Fobj(m):
    return (sum( m.p_cens * m.v_pns[p] + \
                 sum( m.p_f[t] * \
                      ( m.p_beta[t]  * m.v_u[t,p] + \
                        m.p_gamma[t] * m.v_y[t,p] + \
                        m.p_theta[t] * m.v_z[t,p] + \
                        m.p_alfa[t] * m.v_q[t,p] / m.p_k[t]) + \
                        m.p_o[t] * m.v_q[t,p] / m.p_k[t] for t in m.t) for p in m.p))
m.ObjectiveFunction =Objective(rule = e_Fobj, sense = minimize)


def e_DeltaQDefinition(m,t,p): #6
    return (m.v_q[t,p] == m.v_u[t,p] * m.p_k[t] * m.p_qmin[t] + m.v_deltaq[t,p])
m.DeltaQDefinition = Constraint(m.t, m.p, rule=e_DeltaQDefinition)

def e_DeltaQBounds(m,t,p): #7
    return (m.v_deltaq[t,p] <= m.v_u[t,p] * m.p_k[t] * (m.p_qmax[t] - m.p_qmin[t]))
m.DeltaQBounds = Constraint(m.t, m.p, rule = e_DeltaQBounds)
#
# ###Añadir maintenance rule eq 8 pag 17 de 64
#
def e_RampingUpConstraint(m,t,p): #9
    if p != m.p.first():
        return (m.v_deltaq[t,p] - m.v_deltaq[t,m.p.prev(p,1)] <= m.p_rs[t])
    else:
        return Constraint.Skip
m.RampingUpConstraint = Constraint(m.t, m.p, rule = e_RampingUpConstraint)

def e_RampingDownConstraint(m,t,p): #10
    if p != m.p.first():
        return (m.v_deltaq[t,m.p.prev(p,1)]-m.v_deltaq[t,p] <= m.p_rb[t])
    else:
        return Constraint.Skip
m.RampingDownConstraint = Constraint(m.t, m.p, rule = e_RampingDownConstraint)

def e_UnitCommitmentConsistency(m,t,p): #11
    if p != m.p.first():
     return (m.v_y[t,p] - m.v_z[t,p] == m.v_u[t,p] - m.v_u[t,m.p.prev(p,1)])
    else:
        return (m.v_y[t,p] - m.v_z[t,p] == m.v_u[t,p] - m.p_u0[t])
m.UnnitCommitmentConsistency = Constraint(m.t, m.p, rule = e_UnitCommitmentConsistency)

def e_WaterReserves(m,h,p): #16
    if p == m.p.first():
        return (m.v_w[h,p] == m.p_w0[h] - ( m.v_q[h,p] + m.v_s[h,p] - m.p_rend[h] * m.v_b[h,p] ) + m.p_i[p,h] )
    else:
        return (m.v_w[h, p] == m.v_w[h, m.p.prev(p, 1)] - (m.v_q[h, p] + m.v_s[h, p] - m.p_rend[h] * m.v_b[h, p]) + m.p_i[p, h])
m.WaterReserves = Constraint(m.h, m.p, rule = e_WaterReserves)

def e_FinalWaterReserves(m,h,p):
    if p == m.p.last():
        return (m.v_w[h,p] == m.p_wfin[h])
    else:
        return Constraint.Skip
m.FinalWaterReserves = Constraint(m.h,m.p, rule = e_FinalWaterReserves)
#
def e_HydroOutputUpperLimit(m,h,p): #17
    return (m.v_q[h,p] <= m.p_k[h] * m.p_qmax[h])
m.HydroOutputUpperLimit = Constraint (m.h, m.p, rule = e_HydroOutputUpperLimit)

#
def e_PumpingUpperLimit(m,h,p): # 19
    return (m.v_b[h,p] <= m.p_bmax[h])
m.PumpingUpperLimit = Constraint(m.h, m.p, rule = e_PumpingUpperLimit)
#
def e_WaterReserveLowerVolumeLimit(m,h,p): #20
    return (m.p_wmin[h] <= m.v_w[h,p])
m.WaterReserveLowerVolumeLimit = Constraint(m.h, m.p, rule = e_WaterReserveLowerVolumeLimit)
#
def e_WaterReserveUpperVolumeLimit(m, h, p): #20
    return (m.v_w[h,p] <= m.p_wmax[h])
m.WaterReserveUpperVolumeLimit = Constraint(m.h, m.p, rule=e_WaterReserveUpperVolumeLimit)

def e_SolarPowerUpperLimit(m,p):#0.2
    return (m.v_solar[p] <= m.p_solar[p] * 0.2)
m.SolarPowerUpperLimit = Constraint(m.p, rule=e_SolarPowerUpperLimit)

def e_WindPowerUpperLimit(m,p):
    return (m.v_wind[p] <= m.p_wind[p] * 0.3)#0.3
m.WindPowerUpperLimit = Constraint(m.p, rule=e_WindPowerUpperLimit)

def e_DemandBalance(m,p):
    return ( sum(m.v_q[t,p] for t in m.t ) + sum(m.v_q[h,p] - m.v_b[h,p] for h in m.h)+ m.v_wind[p] + m.v_solar[p] + m.v_pns[p] == m.p_d[p])
m.DemandBalance = Constraint(m.p,rule=e_DemandBalance)

def e_SpinningReserve(m,p):
    return ( sum(m.v_u[t,p] * m.p_k[t] * m.p_qmax[t] - m.v_q[t,p] for t in m.t) >= m.p_rod[p])
m.SpinningReserve = Constraint(m.p,rule = e_SpinningReserve)

data = DataPortal()




# p_list = []
# list1 = []
# list2 = []
# list3 = []
# for p in range(1,169):
#     p_list.append('p'+str(p))
#     list1.append(0.01)
#     list2.append(0.5*math.exp(-(p-1)/100))
#     list3.append(0)
#
# dict = {'p':p_list,'HYDRO_RES':list1,'HYDRO_ROR':list2,'HYDRO_PUM':list3}
#
# df = pd.DataFrame(dict)
#
# print(df)
# df.to_csv('Inflows.csv', index = False)

# df = pd.read_csv(str(str(path_model_in_par.joinpath('Data_Demands.csv'))))
# df['p_d'] = df['p_d'].map(lambda p_d: p_d * 0.01)
# df.rename(columns = {'p_d':'p_rod'}, inplace = True)
# df.to_csv(str(path_model_in_par.joinpath('SpinningReserve.csv')), index = False)
# print(df)


#data.load(filename='gens.dat',set=m.g)

# Load of sets
data.load(filename=str(path_model_in_set.joinpath('g.csv')), format='set',set='g')
data.load(filename=str(path_model_in_set.joinpath('d.csv')), format='set',set='d')
data.load(filename=str(path_model_in_set.joinpath('p.csv')), format='set',set='p')

# Load of parameters
data.load(filename=str(path_model_in_par.joinpath('Generators.csv')), index=['g'], param=['p_alfa','p_beta','p_gamma','p_theta','p_rs','p_rb','p_f','p_o','p_qmax','p_qmin','p_u0','p_modo','p_bmax','p_wmax','p_w0','p_wmin','p_wfin','p_k','p_rend','p_type'])
data.load(filename=str(path_model_in_par.joinpath('Demand.csv')), index=['p'], param='p_d')
# data.load(filename=str(path_model_in_par.joinpath('Scalars.csv')), param=['p_cens'])
data.load(filename=str(path_model_in_par.joinpath('Wind.csv')), param=['p_wind'])
data.load(filename=str(path_model_in_par.joinpath('Solar.csv')), param=['p_solar'])
data.load(filename=str(path_model_in_par.joinpath('Inflows.csv')),index=['p','g'],param = ['p_i'], format = 'array')
data.load(filename=str(path_model_in_par.joinpath('SpinningReserve.csv')),index=['p'],param = ['p_rod'])

instance = m.create_instance(data)

solver = SolverFactory('glpk')
solver.options['mipgap'] = 0.1
instance.dual = Suffix(direction=Suffix.IMPORT)
solver_results = solver.solve(instance, tee=False)
solver_results.write()  # Resumen de los resultados del solver
instance.solutions.load_from(solver_results)  # Necesario para fijar los valores de las variables binarias


df = pd.DataFrame.from_dict(instance.v_q.extract_values(), orient='index', columns=[str(instance.v_q)])
df.index.names = ['Generator-Period']
df.reset_index(inplace=True)
df[['Generator', 'Period']] = pd.DataFrame(df['Generator-Period'].tolist())
df['Period'] = pd.Categorical(df['Period'], categories=['p' + str(i) for i in range(1, 169)], ordered=True)
df = df.sort_values('Period')
df_out = df.pivot(index='Period', columns='Generator', values='v_q')
# generator_order = ['HYDRO_PUM', 'HYDRO_ROR', 'HYDRO_RES', 'GAS', 'FUELOIL', 'CCGT', 'ANTHRACITE', 'BITUMINOUS', 'SUBBITUMIN', 'LIGNITE', 'NUCLEAR']
generator_order=['NUCLEAR', 'LIGNITE', 'SUBBITUMIN', 'BITUMINOUS', 'ANTHRACITE', 'CCGT', 'FUELOIL', 'GAS', 'HYDRO_RES', 'HYDRO_ROR','HYDRO_PUM']
df_out = df_out.reindex(columns=generator_order)

solar_data = pd.DataFrame.from_dict(instance.v_solar.extract_values(), orient='index', columns=[str(instance.v_solar)])
solar_data.index.names = ['Period']
solar_data.reset_index(inplace=True)
solar_data = solar_data.rename(columns={'v_solar': 'SOLAR'})
merge_solar = pd.merge(df_out, solar_data, left_index=True, right_on='Period')
merge_solar.set_index('Period', inplace=True)

wind_data = pd.DataFrame.from_dict(instance.v_wind.extract_values(), orient='index',columns=[str(instance.v_wind)])
wind_data.index.names = ['Period']
wind_data.reset_index(inplace=True)
wind_data = wind_data.rename(columns={'v_wind': 'WIND'})
merge_wind = pd.merge(merge_solar, wind_data, left_index=True, right_on='Period')
merge_wind.set_index('Period', inplace=True)

pns_data = pd.DataFrame.from_dict(instance.v_pns.extract_values(), orient='index',columns=[str(instance.v_pns)])
pns_data.index.names = ['Period']
pns_data.reset_index(inplace=True)
pns_data = pns_data.rename(columns={'v_pns': 'PNS'})
merged_data = pd.merge(merge_wind, pns_data, left_index=True, right_on='Period')
merged_data.set_index('Period', inplace=True)


demand_df = pd.DataFrame.from_dict(instance.p_d.extract_values(), orient='index', columns=[str(instance.p_d)])
demand_df.index.names = ['Period']
demand_df.reset_index(inplace=True)
demand_df = demand_df.rename(columns={'p_d': 'Demand'})

generators_df = merged_data

merged_data = pd.merge(merged_data, demand_df, left_index=True, right_on='Period')
merged_data.set_index('Period', inplace=True)
df = pd.DataFrame.from_dict(instance.v_w.extract_values(), orient='index', columns=[str(instance.v_w)])
df = df.dropna()
df.index.names = ['Generator-Period']
df.reset_index(inplace=True)
df[['Generator', 'Period']] = pd.DataFrame(df['Generator-Period'].tolist())
df['Period'] = pd.Categorical(df['Period'], categories=['p' + str(i) for i in range(1, 169)], ordered=True)
df = df.sort_values('Period')
df_out = df.pivot(index='Period', columns='Generator', values='v_w')
df_out = df_out.drop(columns='HYDRO_ROR')
df_pum = df_out.drop(columns='HYDRO_RES')
df_res = df_out.drop(columns='HYDRO_PUM')

df_pum.rename(columns={'HYDRO_PUM':'Water_PUM'}, inplace = True)
df_res.rename(columns={'HYDRO_RES':'Water_RES'}, inplace = True)

reserves_df = pd.merge(df_pum, df_res, left_index=True, right_on='Period')

merged_data = pd.merge(merged_data, reserves_df, left_index=True, right_on='Period')
from pyomo.environ import *
from pathlib import Path
# import gurobipy
# Output figures
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pyomo.environ import Reals, PositiveReals, NonPositiveReals, NegativeReals, NonNegativeReals, PercentFraction, \
    UnitInterval, Integers, PositiveIntegers, NonPositiveIntegers, NegativeIntegers, NonNegativeIntegers, Binary
# import time
# Data management and treatment
import pandas as pd

path_model_in_set = Path('Data/Input/Sets/')
path_model_in_par = Path('Data/Input/Parameters/')
path_model_out    = Path('Data/Output/')
path_results      = Path('Data/Output/')

m = AbstractModel()

#generadores 1,2,3
m.g = Set()
m.d = Set()
m.p = Set(ordered=True)

#Definición de parámetros

#auxiliary load factor
m.p_k = Param(m.g, within = NonNegativeReals)

#Consumo variable de combustible
m.p_alfa = Param(m.g, within = NonNegativeReals)

#Potencia Máxima del generador
m.p_qmax = Param(m.g, within = NonNegativeReals)

#Potencia Mínima del generador
m.p_qmin = Param(m.g, within = NonNegativeReals)

#Demanda del sistema
m.p_d = Param(m.p,within = NonNegativeReals)

#Coste del combustible €/MW
m.p_f = Param(m.g, within = NonNegativeReals)

#Coste de arranque
m.p_ca = Param(m.g, within = NonNegativeReals)

#Emisiones
m.p_e = Param(m.g, within = NonNegativeReals)

#Coste emisiones
m.p_ce = Param(m.g, within = NonNegativeReals)

#rampa subida
m.p_rs = Param(m.g, within = NonNegativeReals)

#rampa bajada
m.p_rb = Param(m.g, within = NonNegativeReals)

#Beta
m.p_beta = Param(m.g, within = NonNegativeReals)

#Gamma
m.p_gamma = Param(m.g, within = NonNegativeReals)

#Theta
m.p_theta = Param(m.g, within = NonNegativeReals)

#Rendimiento de bombeo de una hydro
m.p_rend = Param(m.g, within  = NonNegativeReals)

#Inflows en el embalse h durante el periodo p
m.p_i = Param (m.p, m.g, within = NonNegativeReals)

#Agua Inicial en una reserva hydro
m.p_w0 = Param (m.g, within = NonNegativeReals)

#Agua final en una reserva
m.p_wfin = Param(m.g, within = NonNegativeReals)

#Limite max de bombeo
m.p_bmax = Param (m.g, within = NonNegativeReals)

#Max water capacity
m.p_wmax = Param (m.g, within = NonNegativeReals)

#Min water amount
m.p_wmin = Param (m.g, within = NonNegativeReals)

#Reserva Rodante
m.p_rod = Param (m.p, within = NonNegativeReals, mutable = True, default = 0)

#Coste de demanda no servida
m.p_cens = Param (within = NonNegativeReals,initialize=180.0)

#Tipo de generador: thermal o hydro
m.p_type = Param(m.g, within = Any)

#Potencia Solar disponible durante el periodo p
m.p_solar = Param(m.p,within = NonNegativeReals)

#Potencia eólica disponible durante el periodo p
m.p_wind = Param(m.p, within= NonNegativeReals)

#Estado de acoplamiento del generador en instante inicial
m.p_u0 = Param(m.g, within = Binary)

#Cantidad mínima de flujo de agua en hydro h en periodo p
m.p_flu = Param(m.g,m.p, within = NonNegativeReals)
m.p_o = Param(m.g, within = NonNegativeReals)


#Definición de variables

#Variable de arranque de un grupo
m.v_y = Var(m.g, m.p, within=Binary)

#Variable de parada de un grupo
m.v_z = Var(m.g,m.p, within=Binary)

#Variable de unit commitment
m.v_u = Var(m.g, m.p, within=Binary)

#Potencia generada por grupo en un periodo
m.v_q = Var(m.g, m.p, within=NonNegativeReals)

#Exceso de potencia generada sobre minimo tecnico
m.v_deltaq = Var(m.g, m.p,within=NonNegativeReals)

#Energy stored in water
m.v_w = Var(m.g, m.p, within = NonNegativeReals)

#Spills de una reserva hydro
m.v_s = Var(m.g, m.p, within = NonNegativeReals)

#Bombeo en una reserva hydro
m.v_b = Var(m.g, m.p, within = NonNegativeReals)

#Cantidad de potencia solar utilizada en el periodo p
m.v_solar = Var(m.p, within = NonNegativeReals)

#Cantidad de potencia eólica utilizada en el periodo p
m.v_wind = Var(m.p, within = NonNegativeReals)

#Potencia no servida
m.v_pns = Var(m.p, within = NonNegativeReals)

# %% Declaration of dynamic sets
def setdin_thermal_generators(m, g):
    return m.p_type[g] == 'thermal'
m.t = Set(ordered=True, initialize=m.g, filter=setdin_thermal_generators, doc="Thermal generators")


def setdin_hydro_generators(m, g):
    return m.p_type[g] == 'hydro'
m.h = Set(ordered=True, initialize=m.g, filter=setdin_hydro_generators, doc="Hydro generators")


#Definición de función objetivo

def e_Fobj(m):
    return (sum( m.p_cens * m.v_pns[p] + \
                 sum( m.p_f[t] * \
                      ( m.p_beta[t]  * m.v_u[t,p] + \
                        m.p_gamma[t] * m.v_y[t,p] + \
                        m.p_theta[t] * m.v_z[t,p] + \
                        m.p_alfa[t] * m.v_q[t,p] / m.p_k[t]) + \
                        m.p_o[t] * m.v_q[t,p] / m.p_k[t] for t in m.t) for p in m.p))
m.ObjectiveFunction =Objective(rule = e_Fobj, sense = minimize)


def e_DeltaQDefinition(m,t,p): #6
    return (m.v_q[t,p] == m.v_u[t,p] * m.p_k[t] * m.p_qmin[t] + m.v_deltaq[t,p])
m.DeltaQDefinition = Constraint(m.t, m.p, rule=e_DeltaQDefinition)

def e_DeltaQBounds(m,t,p): #7
    return (m.v_deltaq[t,p] <= m.v_u[t,p] * m.p_k[t] * (m.p_qmax[t] - m.p_qmin[t]))
m.DeltaQBounds = Constraint(m.t, m.p, rule = e_DeltaQBounds)
#
# ###Añadir maintenance rule eq 8 pag 17 de 64
#
def e_RampingUpConstraint(m,t,p): #9
    if p != m.p.first():
        return (m.v_deltaq[t,p] - m.v_deltaq[t,m.p.prev(p,1)] <= m.p_rs[t])
    else:
        return Constraint.Skip
m.RampingUpConstraint = Constraint(m.t, m.p, rule = e_RampingUpConstraint)

def e_RampingDownConstraint(m,t,p): #10
    if p != m.p.first():
        return (m.v_deltaq[t,m.p.prev(p,1)]-m.v_deltaq[t,p] <= m.p_rb[t])
    else:
        return Constraint.Skip
m.RampingDownConstraint = Constraint(m.t, m.p, rule = e_RampingDownConstraint)

def e_UnitCommitmentConsistency(m,t,p): #11
    if p != m.p.first():
     return (m.v_y[t,p] - m.v_z[t,p] == m.v_u[t,p] - m.v_u[t,m.p.prev(p,1)])
    else:
        return (m.v_y[t,p] - m.v_z[t,p] == m.v_u[t,p] - m.p_u0[t])
m.UnnitCommitmentConsistency = Constraint(m.t, m.p, rule = e_UnitCommitmentConsistency)

def e_WaterReserves(m,h,p): #16
    if p == m.p.first():
        return (m.v_w[h,p] == m.p_w0[h] - ( m.v_q[h,p] + m.v_s[h,p] - m.p_rend[h] * m.v_b[h,p] ) + m.p_i[p,h] )
    else:
        return (m.v_w[h, p] == m.v_w[h, m.p.prev(p, 1)] - (m.v_q[h, p] + m.v_s[h, p] - m.p_rend[h] * m.v_b[h, p]) + m.p_i[p, h])
m.WaterReserves = Constraint(m.h, m.p, rule = e_WaterReserves)

def e_FinalWaterReserves(m,h,p):
    if p == m.p.last():
        return (m.v_w[h,p] == m.p_wfin[h])
    else:
        return Constraint.Skip
m.FinalWaterReserves = Constraint(m.h,m.p, rule = e_FinalWaterReserves)
#
def e_HydroOutputUpperLimit(m,h,p): #17
    return (m.v_q[h,p] <= m.p_k[h] * m.p_qmax[h])
m.HydroOutputUpperLimit = Constraint (m.h, m.p, rule = e_HydroOutputUpperLimit)

#
def e_PumpingUpperLimit(m,h,p): # 19
    return (m.v_b[h,p] <= m.p_bmax[h])
m.PumpingUpperLimit = Constraint(m.h, m.p, rule = e_PumpingUpperLimit)
#
def e_WaterReserveLowerVolumeLimit(m,h,p): #20
    return (m.p_wmin[h] <= m.v_w[h,p])
m.WaterReserveLowerVolumeLimit = Constraint(m.h, m.p, rule = e_WaterReserveLowerVolumeLimit)
#
def e_WaterReserveUpperVolumeLimit(m, h, p): #20
    return (m.v_w[h,p] <= m.p_wmax[h])
m.WaterReserveUpperVolumeLimit = Constraint(m.h, m.p, rule=e_WaterReserveUpperVolumeLimit)

def e_SolarPowerUpperLimit(m,p):#0.2
    return (m.v_solar[p] <= m.p_solar[p] * 0.2)
m.SolarPowerUpperLimit = Constraint(m.p, rule=e_SolarPowerUpperLimit)

def e_WindPowerUpperLimit(m,p):
    return (m.v_wind[p] <= m.p_wind[p] * 0.3)#0.3
m.WindPowerUpperLimit = Constraint(m.p, rule=e_WindPowerUpperLimit)

def e_DemandBalance(m,p):
    return ( sum(m.v_q[t,p] for t in m.t ) + sum(m.v_q[h,p] - m.v_b[h,p] for h in m.h)+ m.v_wind[p] + m.v_solar[p] + m.v_pns[p] == m.p_d[p])
m.DemandBalance = Constraint(m.p,rule=e_DemandBalance)

def e_SpinningReserve(m,p):
    return ( sum(m.v_u[t,p] * m.p_k[t] * m.p_qmax[t] - m.v_q[t,p] for t in m.t) >= m.p_rod[p])
m.SpinningReserve = Constraint(m.p,rule = e_SpinningReserve)

data = DataPortal()




# p_list = []
# list1 = []
# list2 = []
# list3 = []
# for p in range(1,169):
#     p_list.append('p'+str(p))
#     list1.append(0.01)
#     list2.append(0.5*math.exp(-(p-1)/100))
#     list3.append(0)
#
# dict = {'p':p_list,'HYDRO_RES':list1,'HYDRO_ROR':list2,'HYDRO_PUM':list3}
#
# df = pd.DataFrame(dict)
#
# print(df)
# df.to_csv('Inflows.csv', index = False)

# df = pd.read_csv(str(str(path_model_in_par.joinpath('Data_Demands.csv'))))
# df['p_d'] = df['p_d'].map(lambda p_d: p_d * 0.01)
# df.rename(columns = {'p_d':'p_rod'}, inplace = True)
# df.to_csv(str(path_model_in_par.joinpath('SpinningReserve.csv')), index = False)
# print(df)


#data.load(filename='gens.dat',set=m.g)

# Load of sets
data.load(filename=str(path_model_in_set.joinpath('g.csv')), format='set',set='g')
data.load(filename=str(path_model_in_set.joinpath('d.csv')), format='set',set='d')
data.load(filename=str(path_model_in_set.joinpath('p.csv')), format='set',set='p')

# Load of parameters
data.load(filename=str(path_model_in_par.joinpath('Generators.csv')), index=['g'], param=['p_alfa','p_beta','p_gamma','p_theta','p_rs','p_rb','p_f','p_o','p_qmax','p_qmin','p_u0','p_modo','p_bmax','p_wmax','p_w0','p_wmin','p_wfin','p_k','p_rend','p_type'])
data.load(filename=str(path_model_in_par.joinpath('Demand.csv')), index=['p'], param='p_d')
# data.load(filename=str(path_model_in_par.joinpath('Scalars.csv')), param=['p_cens'])
data.load(filename=str(path_model_in_par.joinpath('Wind.csv')), param=['p_wind'])
data.load(filename=str(path_model_in_par.joinpath('Solar.csv')), param=['p_solar'])
data.load(filename=str(path_model_in_par.joinpath('Inflows.csv')),index=['p','g'],param = ['p_i'], format = 'array')
data.load(filename=str(path_model_in_par.joinpath('SpinningReserve.csv')),index=['p'],param = ['p_rod'])

instance = m.create_instance(data)

solver = SolverFactory('glpk')
solver.options['mipgap'] = 0.1
instance.dual = Suffix(direction=Suffix.IMPORT)
solver_results = solver.solve(instance, tee=True)
solver_results.write()  # Resumen de los resultados del solver
instance.solutions.load_from(solver_results)  # Necesario para fijar los valores de las variables binarias

df = pd.DataFrame.from_dict(instance.v_q.extract_values(), orient='index', columns=[str(instance.v_q)])
df.index.names = ['Generator-Period']
df.reset_index(inplace=True)
df[['Generator', 'Period']] = pd.DataFrame(df['Generator-Period'].tolist())
df['Period'] = pd.Categorical(df['Period'], categories=['p' + str(i) for i in range(1, 169)], ordered=True)
df = df.sort_values('Period')
df_out = df.pivot(index='Period', columns='Generator', values='v_q')
# generator_order = ['HYDRO_PUM', 'HYDRO_ROR', 'HYDRO_RES', 'GAS', 'FUELOIL', 'CCGT', 'ANTHRACITE', 'BITUMINOUS', 'SUBBITUMIN', 'LIGNITE', 'NUCLEAR']
generator_order=['NUCLEAR', 'LIGNITE', 'SUBBITUMIN', 'BITUMINOUS', 'ANTHRACITE', 'CCGT', 'FUELOIL', 'GAS', 'HYDRO_RES', 'HYDRO_ROR','HYDRO_PUM']
df_out = df_out.reindex(columns=generator_order)

solar_data = pd.DataFrame.from_dict(instance.v_solar.extract_values(), orient='index', columns=[str(instance.v_solar)])
solar_data.index.names = ['Period']
solar_data.reset_index(inplace=True)
solar_data = solar_data.rename(columns={'v_solar': 'SOLAR'})
merge_solar = pd.merge(df_out, solar_data, left_index=True, right_on='Period')
merge_solar.set_index('Period', inplace=True)

wind_data = pd.DataFrame.from_dict(instance.v_wind.extract_values(), orient='index',columns=[str(instance.v_wind)])
wind_data.index.names = ['Period']
wind_data.reset_index(inplace=True)
wind_data = wind_data.rename(columns={'v_wind': 'WIND'})
merge_wind = pd.merge(merge_solar, wind_data, left_index=True, right_on='Period')
merge_wind.set_index('Period', inplace=True)

pns_data = pd.DataFrame.from_dict(instance.v_pns.extract_values(), orient='index',columns=[str(instance.v_pns)])
pns_data.index.names = ['Period']
pns_data.reset_index(inplace=True)
pns_data = pns_data.rename(columns={'v_pns': 'PNS'})
merged_df = pd.merge(merge_wind, pns_data, left_index=True, right_on='Period')
merged_df.set_index('Period', inplace=True)


demand_df = pd.DataFrame.from_dict(instance.p_d.extract_values(), orient='index', columns=[str(instance.p_d)])
demand_df.index.names = ['Period']
demand_df.reset_index(inplace=True)
demand_df = demand_df.rename(columns={'p_d': 'Demand'})

generators_df = merged_df

merged_df = pd.merge(merged_df, demand_df, left_index=True, right_on='Period')
merged_df.set_index('Period', inplace=True)
df = pd.DataFrame.from_dict(instance.v_w.extract_values(), orient='index', columns=[str(instance.v_w)])
df = df.dropna()
df.index.names = ['Generator-Period']
df.reset_index(inplace=True)
df[['Generator', 'Period']] = pd.DataFrame(df['Generator-Period'].tolist())
df['Period'] = pd.Categorical(df['Period'], categories=['p' + str(i) for i in range(1, 169)], ordered=True)
df = df.sort_values('Period')
df_out = df.pivot(index='Period', columns='Generator', values='v_w')
df_out = df_out.drop(columns='HYDRO_ROR')
df_pum = df_out.drop(columns='HYDRO_RES')
df_res = df_out.drop(columns='HYDRO_PUM')

df_pum.rename(columns={'HYDRO_PUM':'Water_PUM'}, inplace = True)
df_res.rename(columns={'HYDRO_RES':'Water_RES'}, inplace = True)

reserves_df = pd.merge(df_pum, df_res, left_index=True, right_on='Period')

merged_df = pd.merge(merged_df, reserves_df, left_index=True, right_on='Period')

merged_df.to_csv('Data/Output/Merged.csv')
reserves_df.to_csv('Data/Output/Reserves.csv')
generators_df.to_csv('Data/Output/Generation.csv')
demand_df.to_csv('Data/Output/Demand.csv')
