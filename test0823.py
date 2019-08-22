# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 21:36:57 2019

@author: SJ
"""

import numpy as np
import pickle
import scipy

def corr(a,b,doy):
    elliptical_orbit_correction = 0.03275104*np.cos(doy/59.66638337) + 0.96804905
    a *= elliptical_orbit_correction
    b *= elliptical_orbit_correction
    return a,b


fpath = r'E:\S2A_MSI\Continental\view_zenith_0\lut\iLUTs\S2A_MSI_02.ilut'

with open(fpath,"rb") as ilut_file:
    iLUT = pickle.load(ilut_file)
    
''' 
solar zentith [degrees] (0 - 75)
water vapour [g/m2] (0 - 8.5)
ozone [cm-atm] (0 - 0.8)
aerosol optical thickness [unitless] (0 - 3)
surface altitude [km] (0 - 7.75)
'''


aots = [0.125, 0.375, 0.625, 0.875, 1.125, 1.375, 1.875, 2.625]

sz = 60
wv = 5
o3 = 0.3
aot = 0.5
km = 0.2  
a, b = iLUT(sz, wv, o3, aot, km)
doy = 154

#%%
Ls = np.arange(1,100,0.1)
aots = np.arange(0.01,2.0,0.02)
#sr = (L-a)/b

#%%
ab = []
if True:
    for aot in aots:
        a,b = iLUT(sz, wv, o3, aot, km)
        a,b = corr(a,b,doy)
        ab.append([a,b,aot])

Ls = np.arange(1,100,0.1)
tb = np.zeros([Ls.shape[0],len(ab)+1])
count = 0
tb[:,0] = Ls
for each in ab:
    count += 1
    tb[:,count] = (Ls - each[0])/each[1]
    
    

    
    
