import pandas as pd
import numpy as np
import re

def load(filepaths, offsettime = None, sub_lowpow = False):

    params = pd.read_csv(filepaths[0], nrows = 11, usecols = [1])
    params = params.transpose()
    amp = float(params['Amplification'][0]) # Is amplification already taken into account?
    K = float(params['K'][0])
    back_V = params['Background Voltage'][0].replace('V','')
    unitdict = {'m':1e-3, 'u':1e-6}
    scale = unitdict[back_V[-1]]
    back_V = float(back_V[:len(back_V)-1])*scale # remove mV or uV and scale appropriately

    # time = pd.read_csv(filepaths[0], skiprows = 13)['Time(s)']
    V1 = pd.read_csv(filepaths[-1], skiprows = 13,index_col = 0)['Voltage (V)']
    time  = V1.index
    df_V= pd.DataFrame(index = time)
    fluences = pd.Series(index = filepaths)
    for filepath in filepaths:

        temp = pd.read_csv(filepath, skiprows = 13, index_col=0)
        volt = temp['Voltage (V)']
        if(sub_lowpow):
            volt = volt -V1
        df_V = pd.concat([df_V, volt], axis = 1)
        
        m = re.search('Fluence=(.+?)_',filepath) # Read fluence from filename
        if m:
            fluences[filepath] = m.group(1)
    df_V.columns = fluences
    if offsettime is not None:
        df_V = df_V - np.mean(df_V[0:offsettime])

    df_cond = convert_V2cond(df_V,back_V,K)

    return df_V, df_cond

def load_fluence(filepath):
    """Fluence file was not included in all experiments?"""
    filepath = 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\High_Power_3_FluenceSweep.csv'
    fluencesweep = pd.read_csv(filepath, skiprows = 13)
    fluences = fluencesweep['Fluence(cm^-2)']
    return fluences

def convert_V2cond(df_V,back_V,K):
    df_cond = - ((df_V)/back_V)/K
    return df_cond

def maxG_and_fom(df_cond, params):
    
    beta = params['beta']
    e = 1.6e-19
    FA = params['FA']
    M = params['M']

    fluences = df_cond.columns
    maxG = pd.Series(index = fluences)
    fom = pd.Series(index = fluences)

    for fluence in fluences:
        maxG[fluence] = df_cond[fluence].max()
        fom[fluence] =  maxG[fluence]/(beta*e*fluence*FA*M)

    return maxG, fom