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
    f_in.close()

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
   
    fname = './fcode.txt'
    fcode_lst = load_fcode()
    #today = '2017-03-31'
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    wset_data= w.wset("sectorconstituent","date=" + today + ";sectorid=a001010100000000;field=wind_code")
    if (wset_data.ErrorCode != 0):
        sys.stderr.write("Error in get new fcode!")
    else:    
        new_fcode_lst = wset_data.Data[0]
        for fcode in fcode_lst:
            if fcode in new_fcode_lst:
			    new_fcode_lst.remove(fcode)
        print 'Newly added fcode: ' + str(len(new_fcode_lst))
        fm = pd.Series(new_fcode_lst)
        with open(fname, 'a+') as f:
            fm.to_csv(f, sep='|', index=False, header=False)
    
    w.stop()


