import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import pandas as pd
np.random.seed(8675309) # set random seed

expt_info  = pd.read_excel('./experiment info.xlsx')

def calc_dummy_data(t,C,P,T):
    r = -0.1*P*np.exp(5000*(-1/(T+273.15)+1/(300)))*C
    return(r)

for ix,e,T,P,c in expt_info.itertuples():
    c0 = [c]
    sol = solve_ivp(lambda t,y: calc_dummy_data(t,y,P,T),[0,50],c0,t_eval = np.arange(0,30,5))
    df = pd.DataFrame({'Time':sol.t.reshape(-1),
                       'Response':((c0-sol.y.T.reshape(-1))*np.random.uniform(0.1,0.12,size=len(sol.y.T))).round(decimals = 1)})
    df.to_excel(f'./experiment {str(e)}.xlsx',index=False)

df.plot('Time','Response')