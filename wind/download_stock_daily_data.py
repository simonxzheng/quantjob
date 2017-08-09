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

#
# Utility function
#
def load_fcode():

    fname = "D:\\sharedata\\fcode.txt"
    
    close_lst = []
    amt_lst = []
    fdate_lst = []
    cnt_err = 0
    f_in = open(fname)
    fcode_lst = []
    for line in f_in:
        try:
            items = line.strip().split(',')
            if len(items) < 1:
                continue
            fcode_lst.append(items[0])
            
        except ValueError:
            cnt_err += 1
            continue

    return fcode_lst

#
# download single day data
#
def get_field_data(fcode_lst, field, fdate):
    
    wsd_data = w.wsd(fcode_lst, field, fdate, fdate, "PriceAdj=B") 
    if (wsd_data.ErrorCode != 0):
        sys.stdout.write("Error in getting market quote!")
        return None
    return wsd_data.Data[0]

            
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
   
    fname = './hfq2016_wind.txt'
    fcode_lst = load_fcode()
    fdate = options.startdate #'2017-05-12'
    #fdate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    pre_close = get_field_data(fcode_lst, 'pre_close', fdate)
    open = get_field_data(fcode_lst, 'open', fdate)
    close = get_field_data(fcode_lst, 'close', fdate)
    high = get_field_data(fcode_lst, 'high', fdate)
    low = get_field_data(fcode_lst, 'low', fdate)
    volume = get_field_data(fcode_lst, 'volume', fdate)
    maxupordown = get_field_data(fcode_lst, 'maxupordown', fdate)
    susp_days = get_field_data(fcode_lst, 'susp_days', fdate)

    df = pd.DataFrame({ 'fdate' : fdate,
                        'fcode' : fcode_lst,
                        'pre_close' : pre_close,
                        'open' : open,
                        'close' : close,
                        'high' : high,
                        'low' : low,
                        'volume': volume,
                        'maxupordown': maxupordown,
                        'susp_days': susp_days})
    
    ndf = df[['fdate', 'fcode', 'pre_close', 'open', 'close', 'high', 'low', 'volume', 'maxupordown', 'susp_days']]

    print "#: ", len(ndf)
    print "close: ", len(ndf[ndf.close > 0])
    print "volume",	len(ndf[ndf.volume > 0])
    print "Maxupordown: ", len(ndf[ndf.maxupordown == 1])
    print "Suspending: ", len(ndf[ndf.susp_days > 0])
    print "NA volume: ", len(ndf[pd.isnull(ndf.volume)])

    #with open(fname, 'a') as f:
    #ndf.to_csv(fname, index=False, header=True, sep='|')

    adf = pd.read_csv(fname, sep='|', index_col=None, header=None)
    adf.columns = ['fdate', 'fcode', 'pre_close', 'open', 'close', 'high', 'low', 'volume', 'maxupordown', 'susp_days']
    adf = adf[adf.fdate != '2017-06-03'] #filter
    bdf = adf.append(ndf)
    sdf = bdf.sort_values(by=['fcode', 'fdate'], ascending=[True, True])
    sdf.to_csv(fname, sep='|', index=False, header=False)
    
    w.stop()
