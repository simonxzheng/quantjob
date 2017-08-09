#!/usr/bin/env python
# -*- coding: utf-8 -*-
from WindPy import w
import math
import os
import sys
import datetime
import copy
import numpy as np
import time
from optparse import OptionParser
import pandas as pd
import pdb
import util

#global variable
LABEL_SIGNAL=80
A=0.05
B=-0.03
C=0.05

def calc_zhangting(close_lst, fmax, fmin):

    ZHANGTING_PCT = 0.099
    DIETING_PCT = -0.099
    zt_flag = 0
    dt_flag = 0
    
    if (len(close_lst) < 2):
        return (zt_flag, dt_flag)

    fclose = close_lst[-1]
    fprev_close = close_lst[-2]

    max_chg = fmax / fprev_close - 1.00
    close_chg = fclose / fprev_close - 1.00
               
    if (max_chg < ZHANGTING_PCT):
        zt_flag = 0
    elif (fmin == fmax):
        zt_flag = 1 #yi zi ban
    elif (fclose < fmax):
        zt_flag = 3 #failed raising limit
    else:
        zt_flag = 2 #normal raising limit
                
    if (close_chg < DIETING_PCT):
        dt_flag = 1
    else:
        dt_flag = 0
    
    return (zt_flag, dt_flag)

def shape_long(close_lst, open_lst, vol_lst):
    
    if (len(close_lst) < 4):
        return 0
    
    vol = vol_lst[-1]
    p1_vol = vol_lst[-2]
    p2_vol = vol_lst[-3]

    open = open_lst[-1]
    p1_open = open_lst[-2]
    p2_open = open_lst[-3]
    
    close = close_lst[-1]
    p1_close = close_lst[-2]
    p2_close = close_lst[-3]
    p3_close = close_lst[-4]
    
    p0_chg = close/p1_close - 1.0
    p1_chg = p1_close/p2_close - 1.0
    p2_chg = p2_close/p3_close - 1.0
    p1_open_close = p1_close/p1_open - 1.0 #判断带实体阴线

    #pdb.set_trace()
    max_val = max(np.array(close_lst[-20:]))
    #print p0_chg,p1_chg,p2_chg

    if (p0_chg > A and p1_chg < B and p2_chg > C and p1_chg > -0.099):  #去除跌停股
    #if (p0_chg > A and p1_chg < B and p2_chg > C and p1_open_close < 0 and p1_vol < (vol + p2_vol)*0.75):
        if (close > p2_close):
            if (p2_vol > p1_vol):
                if (close == max_val):
                    flag = 4  # 缩量调整, 创新高，20170112 太阳电缆
                else:
                    flag = 3  # 缩量调整，20170112 闽东电力
            else:
                flag = 2 # 非缩量，上升势
        else:
            flag = 1 #弱信号
    else:
        flag = 0

    return flag

if __name__ == '__main__':
    
    #Parameters from command line
    parser = OptionParser()
    parser.add_option("-c", "--Configfile", dest="configfpath",
                  action="store", type="string", help="Configuration file absolute path")
    parser.add_option("-s", "--Strategy", dest="strategyname",
                  action="store", type="string", help="Strategy name")
    (options, args) = parser.parse_args()
    cf = util.Configuration(options.configfpath, options.strategyname)

    #w.start()
    signal_lst = []
    # input data is ascendingly sorted by portfolioname and then fdate
    curr_fcode = None
    close_lst = []
    open_lst = []
    vol_lst = []
    cnt_err = 0 
    f_in = open(cf.rawdata_file)
    for line in f_in:
        try:
            items = line.strip().split('|')
            if (len(items) < 10 or len(items[3]) == 0):
                continue
            fdate = items[0]
            fcode = items[1]
            prev_close = float(items[2])
            fopen = float(items[3])
            fclose = float(items[4])
            fmax = float(items[5])
            fmin = float(items[6])
            fvol = float(items[7])
            if len(items[8]) > 0:  #not matter what maxupordown flag is
                maxupordown = float(items[8])
            else:
                maxupordown = 0
            susp_days = float(items[9])
            if fvol <= 0:
                continue

            #if (fcode != '601228.SH'): 
            #    continue
            #print fdate, fcode, fclose, fclose / prev_close - 1.0

            if curr_fcode == None:
                curr_fcode = fcode
            if curr_fcode != fcode:
                curr_fcode = fcode
                close_lst = []
                open_lst = []
                vol_lst = []
                
            close_lst.append(fclose)
            open_lst.append(fopen)
            vol_lst.append(fvol)
            
            long_flag = shape_long(close_lst, open_lst, vol_lst)
            if (fdate >= '2016-01-01' and long_flag > 0):
                b = str(fdate)
                signal_lst.append([LABEL_SIGNAL, fdate, options.strategyname, fcode])
            
        except ValueError:
            cnt_err += 1
            continue
  
    if len(signal_lst) > 0:
        df = pd.DataFrame(signal_lst)
        df.columns=['label', 'fdate', 'portfolio_name', 'fcode']
        sdf = df.sort_values(by=['fdate', 'fcode'], ascending=[True, True])
        sdf.to_csv(cf.signalfile, sep='|', index=False, header=False)
    
    #w.stop()
