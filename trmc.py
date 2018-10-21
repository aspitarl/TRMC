import pandas as pd
import numpy as np

def load(filepaths, offsettime = None, sub_lowpow = False):
    
    params = pd.read_csv(filepaths[0], nrows = 11, usecols = [1])
    params = params.transpose()
    amp = float(params['Amplification'][0]) # Is amplification already taken into account?
    K = float(params['K'][0])
    back_V = params['Background Voltage'][0].replace('V','')
    unitdict = {'m':1e-3, 'u':1e-6}
    scale = unitdict[back_V[-1]]
    back_V = float(back_V[:len(back_V)-1])*scale # remove mV or uV and scale appropriately

    time = pd.read_csv(filepaths[0], skiprows = 13)['Time(s)']
    V1 = pd.read_csv(filepaths[-1], skiprows = 13)['Voltage (V)']
    df_V= pd.DataFrame(index = time)

    for filepath in filepaths:
        temp = pd.read_csv(filepath, skiprows = 13)
        volt = temp['Voltage (V)']
        if(sub_lowpow):
            volt = volt -V1
        df_V = pd.concat([df_V, volt], axis = 1)

    if offsettime is not None:
        df_V = df_V - np.mean(df_V[0:offsettime])

    df_cond = convert_V2cond(df_V,back_V,K)

    return df_V, df_cond

def convert_V2cond(df_V,back_V,K):
    df_cond = - ((df_V)/back_V)/K
    return df_cond