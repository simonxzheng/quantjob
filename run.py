#!/usr/bin/env python
# -*- coding: utf-8 -*-
from WindPy import w
import math
import os
import sys
import datetime
import copy
import numpy
import time
import pandas as pd
from optparse import OptionParser
import commands
import pdb

from dataformat import *
import util

# python run.py -s 2016-06-30 -e 2016-07-10
# 
# Traverse portfolio transactions by trading days
#  
def aggregate_portfolio(portfolio_name, portfolio_data, cf, sdate, edate):

    if len(portfolio_data) > 0:
        if sdate == None:
            sdate = portfolio_data[0][trans_fdate]
        if edate == None:
            edate = portfolio_data[-1][trans_fdate]
        
    df = []
    td = util.get_trading_days(sdate, edate)
    i = 0
    for pdate in td:
        trans_data = []
        while i < len(portfolio_data) and pdate == portfolio_data[i][trans_fdate]:
            trans_data.append(portfolio_data[i])
            i += 1
        ldf = aggregate_position(df, portfolio_name, pdate, trans_data, cf)
        df.append(ldf)
        
    return df


if __name__ == '__main__':
    
    #Parameters from command line
    parser = OptionParser()
    parser.add_option("-c", "--Configfile", dest="configfpath",
                  action="store", type="string", help="Configuration file absolute path")
    parser.add_option("-s", "--Strategy", dest="strategyname",
                  action="store", type="string", help="Strategy name")
    parser.add_option("-a", "--Startdate", dest="startdate", 
                  action="store", type="string", help="start portfolio date")  
    parser.add_option("-b", "--Enddate", dest="enddate", 
                  action="store", type="string", help="end portfolio date")
    (options, args) = parser.parse_args()
    cf = util.Configuration(options.configfpath, options.strategyname)

    if options.startdate != None:
        td = util.get_trading_days(options.startdate, options.enddate)
    else:
        today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        td = util.get_trading_days('2016-01-01', today)
        td = td[-2:]

    i = 0
    pdate = td[0]
    fdate = None
    for i in range(1, len(td)):
        fdate = td[i]
        print "-------------------------------------------------------------------------------"
        print pdate, fdate

        print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        start = time.time()
    
        #Step 1
        #cmd = 'python transaction.py -a 2016-12-30 -b 2017-01-03 -s ShortTerm001'
        cmd = "python .\\transaction_" + options.strategyname + ".py -a " + pdate + " -b " + fdate + " -s " + options.strategyname
        print cmd
        a=os.system(cmd)
        print "status:", a

        #Step 2
        #cmd = 'python portfolio.py -a 2016-12-30 -b 2017-01-03 -s ShortTerm001'
        cmd = "python .\\portfolio.py -a " + pdate + " -b " + fdate + " -s " + options.strategyname
        print cmd
        a=os.system(cmd)
        print "status:", a
        
        pdate = fdate

        print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        end = time.time()
        print ("Spent %.1f min" %((end-start)/60.0))
        
