#!/usr/bin/env python
# -*- coding: utf-8 -*-
from WindPy import w
import math
import os
import sys
import datetime
import copy
import time
from optparse import OptionParser
import pandas as pd
import pdb


if __name__ == '__main__':
    
    #Parameters from command line
    parser = OptionParser()
    parser.add_option("-s", "--Startdate", dest="startdate", 
                  action="store", type="string", help="start portfolio date")  
    parser.add_option("-e", "--Enddate", dest="enddate", 
                  action="store", type="string", help="end portfolio date")
    parser.add_option("-c", "--Configfile", dest="configfpath",
                  action="store", type="string", help="Configuration file absolute path")
    (options, args) = parser.parse_args()

    w.start()

    wsd_data = w.wset("carryoutspecialtreatment","startdate=1990-01-01;enddate=2017-02-17;field=wind_code,implementation_date")
    start_fcode_lst = wsd_data.Data[0]
    start_date_lst = [x.strftime('%Y-%m-%d') for x in wsd_data.Data[1]]
    d = {'fcode':start_fcode_lst, 'st_start_date': start_date_lst}
    sdf = pd.DataFrame(d)
    
    wsd_data = w.wset("cancelspecialtreatment","startdate=1990-01-01;enddate=2017-02-17;field=wind_code,implementation_date")
    end_fcode_lst = wsd_data.Data[0]
    end_date_lst = [x.strftime('%Y-%m-%d') for x in wsd_data.Data[1]]
    d = {'fcode':end_fcode_lst, 'st_end_date': end_date_lst}
    edf = pd.DataFrame(d)

    #Merge by the order of date
    #df = pd.merge(sdf, edf, how='left', on=['fcode'])
    fcode_lst = []
    start_date_lst = []
    end_date_lst = []
    for fcode in start_fcode_lst:
        a = sorted(sdf[sdf.fcode == fcode]['st_start_date'].values)
        b = sorted(edf[edf.fcode == fcode]['st_end_date'].values)
        if len(b) == len(a) - 1:
            b.append('2100-01-01')
        for i in range(0, len(a)):
            fcode_lst.append(fcode)
            start_date_lst.append(a[i])
            end_date_lst.append(b[i])
    d = {'fcode':fcode_lst, 'st_end_date': start_date_lst, 'st_end_date': end_date_lst}
    df = pd.DataFrame(d)
    
    #=wset("SectorConstituent","date="&C4,"sector="&C5,"cols=3;rows=3112")

    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    fname = './st_stocks.txt'
    with open(fname, 'w+') as f:
        df.to_csv(f, sep='|', index=False, header=False)
    
    w.stop()
