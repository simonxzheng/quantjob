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
   
    fname = './new_quote.txt'
    fcode_lst = load_fcode()
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    sdate = '2017-01-01'
    edate = '2017-03-24'
    for fcode in fcode_lst:
        sys.stdout.write(fcode + "\n")
        #wsd_data = w.wsd(fcode_lst, "pre_close", sdate, edate, "PriceAdj=B") 
        wsd_data = w.wsd(fcode, "windcode,pre_close,open,close,high,low,volume,maxupordown,susp_days", sdate, edate, "PriceAdj=B") #"Fill=Previous"
        if (wsd_data.ErrorCode != 0):
            sys.stdout.write("Error in getting market quote!")
        else:
            date_lst = [x.strftime('%Y-%m-%d') for x in wsd_data.Times]
            fm = pd.DataFrame(wsd_data.Data,index=wsd_data.Fields,columns=date_lst)
            fm = fm.T
            with open(fname, 'a+') as f:
                fm.to_csv(f, sep='|', header=False)

    #    
    #sdf = df.sort_values(by=['fdate', 'fcode'], ascending=[True, True])
    #sdf.to_csv("./abc.txt", sep='|', index=False, header=False)
    
    w.stop()


