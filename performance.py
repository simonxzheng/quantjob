#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CMD line
# python .\performance.py -b 000001.SH -s 2016-07-01 -e 2017-01-19
from WindPy import w
import math
import os
import sys
import datetime
import copy
import numpy
import time
from optparse import OptionParser
import pdb
import pandas as pd
import matplotlib.pyplot as plt 
    
from dataformat import *
import util

#Global variable

#
# Aggregate performance between [start_date, end_date]
#
def preprocess_data(portfolio_orig, benchmark, start_date, end_date):
    
    # Filter by date range
    portfolio = []
    for i in range(0, len(portfolio_orig)):
        fdate = portfolio_orig[i][port_fdate]
        if start_date == None or end_date == None or (fdate >= start_date and fdate <= end_date):
            portfolio.append(portfolio_orig[i])

    mkt_val_array = []
    lst_date = []
    for i in range(0, len(portfolio)):
        mkt_val_array.append(float(portfolio[i][port_market_value]))
        fdate = portfolio[i][port_fdate]
        lst_date.append(fdate)

    bench_array = []

    w.start()
    wsd_data = w.wsd(benchmark, "close", start_date, end_date, "PriceAdj=B")
    if (wsd_data.ErrorCode != 0):
        print "Error in getting security price!"
    else:
        bench_array = wsd_data.Data[0]
    #w.stop()

    return (lst_date, mkt_val_array, bench_array)

#
# Aggregate performance between [start_date, end_date]
#
def calc_performance(lst_date, mkt_val_array, bench_array):

    mdd = 0
    mdd_j = 0
    for i in range(0, len(mkt_val_array)):
        for j in range(i+1, len(mkt_val_array)):
            drawdown = mkt_val_array[j] / mkt_val_array[i] - 1
            if drawdown < mdd:
                mdd = drawdown
                mdd_j = j
    print mdd_j

    abs_return = 0
    annual_return = 0
    bench_return = 0
    if len(lst_date) > 0:
        d1 = int(lst_date[0].replace('-', ''))
        d2 = int(lst_date[-1].replace('-', ''))
        elapsed_days = util.year_diff(d1, d2, cf.DAYCOUNT)
        abs_return = (mkt_val_array[-1] / mkt_val_array[0] - 1.0)
        annual_return = abs_return / elapsed_days
        bench_return = (bench_array[-1] / bench_array[0] - 1.0) / elapsed_days

    daily_chg = numpy.array(mkt_val_array[1:]) / numpy.array(mkt_val_array[:-1]) - 1.0
    annual_vol = numpy.std(daily_chg, ddof=1) * math.sqrt(cf.ANNUAL_TRADING_DAYS / 1)
    if annual_vol > 0:
        sharp_ratio = (annual_return - cf.RISK_FREE_RATE) / annual_vol 
    else:
        sharp_ratio = 0.0
    
    info_ratio = 0.0
    bench_daily_chg = numpy.array(bench_array[1:]) / numpy.array(bench_array[:-1]) - 1.0
    residual = daily_chg - bench_daily_chg
    track_vol = numpy.std(residual, ddof=1) * math.sqrt(cf.ANNUAL_TRADING_DAYS / 1)
    if track_vol > 0:
        info_ratio = (annual_return - bench_return) / track_vol
    else:
        info_ratio = 0

    x = [daily_chg, bench_daily_chg]
    bench_var = numpy.std(bench_daily_chg, ddof=1) 
    beta = numpy.cov(x)[0][1] / bench_var / bench_var  
    alpha = (annual_return - cf.RISK_FREE_RATE) - beta * (bench_return - cf.RISK_FREE_RATE)
    
    #format and output
    mdd = round(mdd, 4)
    abs_return = round(abs_return, 4)
    annual_return = round(annual_return, 4)
    annual_vol = round(annual_vol, 4)
    sharp_ratio = round(sharp_ratio, 4)
    info_ratio = round(info_ratio, 4)
    beta = round(beta, 5)
    alpha = round(alpha, 4)
    sys.stdout.write( "|".join(['mdd', 'abs_return', 'annual_return', 'annual_vol', 'sharp_ratio', 'info_ratio', 'beta', 'alpha'])+ "\n")
    sys.stdout.write( "|".join([str(mdd), str(abs_return), str(annual_return), str(annual_vol), str(sharp_ratio), str(info_ratio), str(beta), str(alpha)] )+ "\n")

    print mkt_val_array[0], mkt_val_array[-2], mkt_val_array[-1] 
    print round(mkt_val_array[-2] / mkt_val_array[-1] - 1.0, 4),  abs_return
	
    return


if __name__ == '__main__':
    
    #Parameters from command line
    parser = OptionParser()
    parser.add_option("-c", "--Configfile", dest="configfpath",
                  action="store", type="string", help="Configuration file absolute path")
    parser.add_option("-s", "--Strategy", dest="strategyname",
                  action="store", type="string", help="Strategy name")
    parser.add_option("-a", "--Prevdate", dest="startdate",
                  action="store", type="string", help="Previous trading date")
    parser.add_option("-b", "--Currentdate", dest="enddate",
                  action="store", type="string", help="Current trading date")
    parser.add_option("-m", "--Benchmark", dest="benchmark",
                  action="store", type="string", help="Current trading date")
    (options, args) = parser.parse_args()
    cf = util.Configuration(options.configfpath, options.strategyname)

    df = []
    # input data is ascendingly sorted by fdate
    portfolio_data = [] #2d arrays
    cnt_err = 0
    f_in = open(cf.portfile)
    for line in f_in:
    #for line in sys.stdin:
        try:
            items = line.strip().split('|')
            label = int(items[0])
            fdate = items[1]

            if label == Label.PORTFOLIO:
                portfolio_data.append(items)
        except ValueError:
            cnt_err += 1
            continue

    (lst_date, mkt_val_array, bench_array) = preprocess_data(portfolio_data, options.benchmark, options.startdate, options.enddate)
    
    #print lst_date
    #print mkt_val_array
    #print bench_array
    
    calc_performance(lst_date, mkt_val_array, bench_array)

    df = pd.DataFrame({ 'fdate' : lst_date,
                        'portfolio_val' : mkt_val_array,
                        'benchmark' : bench_array})
    ndf = df[['fdate', 'portfolio_val', 'benchmark']]
    ndf.to_csv(cf.valuefile, sep='|', index=False, header=True)


    #pdb.set_trace()
    
    x = range(0, len(lst_date))
    y1 = [k/mkt_val_array[0]*100 - 100 for k in mkt_val_array]
    y2 = [k/bench_array[0]*100 - 100 for k in bench_array]
    
    fig = plt.figure(figsize=(8, 4))
    ax1=fig.add_subplot(111)
    ax1.plot(y1, label="Portfolio Return", color="red", linewidth=2)
    ax1.plot(y2, label="Benchmark", color="blue", linewidth=2)
    #plt.xticks(arange(len(lst_date)), lst_date)
    #plt.xticks(arange(139))
    plt.xticks(fontsize=10, rotation=90)
    locs, labels = plt.xticks()
    print labels
    #plt.figure(figsize=(8,4))
    #plt.plot(x, y1, label="Portfolio Return", color="red", linewidth=2)
    #plt.plot(x, y2, label="Benchmark", color="blue", linewidth=2)     
    plt.xlabel("Date")  
    plt.ylabel("Portfolio Return")  
    plt.title("Portfolio return vs. Benchmark 0000001.SH")  
    plt.ylim(-10, 150)
    import matplotlib.ticker as mtick
    fmt='%.0f%%'
    yticks = mtick.FormatStrFormatter(fmt)
    ax1.yaxis.set_major_formatter(yticks)
    
    legend1=ax1.legend(loc=(.05,.86),fontsize=9,shadow=True)
    legend2=ax1.legend(loc=(.05,.84),fontsize=9,shadow=True)
    legend1.get_frame().set_facecolor('#FFFFFF')
    legend2.get_frame().set_facecolor('#FFFFFF')

    #plt.show()
    pic_path = os.path.join("../data", options.strategyname, "return.png")
    fig.savefig(pic_path, dpi=200)