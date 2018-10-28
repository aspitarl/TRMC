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
    FA = params['FA']*0.9 #0.9 factor from ITO
    M = params['M']

    fluences = df_cond.columns
    maxG = pd.Series(index = fluences)
    fom = pd.Series(index = fluences)

    for fluence in fluences:
        maxG[fluence] = df_cond[fluence].max()
        fom[fluence] =  maxG[fluence]/(beta*e*fluence*FA*M)

    return maxG, fom

def lor(f,f0,w,R0): #Need to check this
    #return 1-(1-R0)*(w)*(w/((f-f0)**2+w**2))
    return (R0 + (2*(f-f0)/w)**2)/(1 + (2*(f-f0)/w)**2)


if __name__ == '__main__':
    filepaths_A = ['C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=01_Fluence=6.45E+14_data.csv','C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=02_Fluence=5.121E+14_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=03_Fluence=4.07E+14_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=04_Fluence=3.231E+14_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=05_Fluence=2.567E+14_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=06_Fluence=2.038E+14_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=07_Fluence=1.619E+14_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=08_Fluence=6.45E+13_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=09_Fluence=3.231E+13_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=10_Fluence=6.45E+12_data.csv', 'C:\\Users\\aspit\\OneDrive\\Data\\TRMC\\Gratzel\\Sample A\\Data\\High_Power_Filter=11_Fluence=6.45E+11_data.csv']
    df_A_V, df_A_cond = load(filepaths_A, offsettime = 50e-9, sub_lowpow = True)
    print(df_A_V)
