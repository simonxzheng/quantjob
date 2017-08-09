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
    
    fname = './stock_deatails.txt'
    fcode_lst = load_fcode()
    for fcode in fcode_lst:
        print(fcode)
        wsd_data = w.wsd(fcode, "windcode,sec_englishname,ipo_date,sec_name", "2017-03-24", "2017-03-24", "")
        if (wsd_data.ErrorCode != 0):
            sys.stdout.write("Error in getting security details!")
        else:
            windcode = wsd_data.Data[0][0]
            ename = wsd_data.Data[1][0]
            ipo_date = wsd_data.Data[2][0].strftime('%Y-%m-%d')
            sec_name = wsd_data.Data[3][0]
            tmp = "|".join([windcode, ename, ipo_date, sec_name]) + "\n"
            with open(fname, 'a+') as f:
                f.write(tmp)
    
    w.stop()
