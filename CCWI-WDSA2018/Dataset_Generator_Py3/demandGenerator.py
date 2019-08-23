# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 15:58:48 2018

@author: mkiria01
"""
import numpy as np
import scipy.io

def genDem():
    weekPat = scipy.io.loadmat('weekPat_30min.mat')
    Aw = weekPat['Aw']
    nw = weekPat['nw']
    yearOffset = scipy.io.loadmat('yearOffset_30min.mat')
    Ay = yearOffset['Ay']
    ny = yearOffset['ny']
     
    # Create yearly component
    days = 365
    
    T=(288/6)*days # one year period in five minute intervals
    w=2*np.pi/T
    k=np.arange(1, days*288/6+1 ,1) # number of time steps in time series
    n=ny[0][0] # number of fourier coefficients
    Hy=[1]*len(k)
    
    for i in range(1,n+1):
        Hy=np.column_stack((Hy, np.sin(i*w*k), np.cos(i*w*k)))
    
    Hy.shape # check size matrix
    uncY=0.1
    AyR = Ay*(1-uncY+2*uncY*np.random.rand(int(Ay.shape[0]),int(Ay.shape[1]))) # randomize fourier coefficients
    yearOffset = np.dot(Hy, AyR)
    
    # Create weekly component
    T=(288/6)*7 #one week period in five minute intervals
    w=2*np.pi/T
    k=np.arange(1, days*288/6+1 ,1) # number of time steps in time series
    n=nw[0][0] # number of fourier coefficients
    Hw=[1]*len(k)
    for i in range(1,n+1):
        Hw=np.column_stack((Hw, np.sin(i*w*k), np.cos(i*w*k)))
    
    uncW=0.1
    AwR = Aw*(1-uncW+2*uncW*np.random.rand(int(Aw.shape[0]),int(Aw.shape[1]))) # randomize fourier coefficients
    weekYearPat = np.dot(Hw, AwR)
    
    # Create random component
    uncR=0.05
    random = np.random.normal(0,(-uncR+2*uncR),(int(weekYearPat.shape[0]),int(weekYearPat.shape[1]))) #normally distributed random numbers
    
    # Create demand
    #blow=30
    #bhigh=35
    base =1#blow+np.random.rand()*(bhigh-blow)
    variation = 0.75+ np.random.normal(0,0.07) # from 0 to 1
    dem = base * (yearOffset+1) * (weekYearPat*variation+1) * (random+1)
    dem = dem.tolist()
    demFinal = []
    for d in dem:
        demFinal.append(d[0])
      
    return demFinal