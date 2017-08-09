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
from optparse import OptionParser
import pdb
import pandas as pd

from dataformat import *
import util

#Global variable
hdf = []

#历史价格
#field: open or close
def get_hist_price_raw(fdate, security, field):

    price = []
    if (len(security) == 0):
        return price

    #Retrieve price from Wind
    wsd_data = w.wsd(security, field, fdate, fdate, "PriceAdj=B")
    if (wsd_data.ErrorCode != 0):
        print 'Error in getting security price!'
    price = wsd_data.Data[0]
    
    return price

    
def load_hfq(csv_fname):

    loc_pred_file = csv_fname
    #loc_pred_file = os.path.join(loc_root, csv_fname)
    df = pd.read_csv(loc_pred_file, sep='|', index_col=None, header=None) #index by fdate
    df.columns = ['fdate', 'fcode', 'pre_close', 'open', 'close', 'high', 'low', 'volume', 'maxupordown', 'susp_days']
    #df = df[df.volume > 0] #remove suspending days

    return df.copy(deep=True)

    
#历史价格 
#field: open or close
def get_hist_price(fdate, security, field):

    price = []
    if (len(security) == 0):
        return price

    #Retrieve price from Wind
    global rdf
    rdf = hdf[hdf['fdate'] == fdate].set_index('fcode')
    data = rdf[field].to_dict()
    for fcode in security:
        if fcode in data:
            price.append(data[fcode])
        else:
            price.append(0)
    
    return price


# 
# Convert trading transactions into portfolio positions
#   format: fdate,model,market_value,cash,pool=stk1:vol1:p_avg1;stk2:vol2:p_avg2;...
#   df: historical portfolio positions
#   trans_data: incremental records
#   position_data: previous trading date positions
# output format:
#   fdate, market_value,cash,{fcode1:position1, fcode2:position2}
#
def aggregate_position(portfolio_name, pdate, fdate, position_data, trans_data, fname):
    
    prev_fdate = None
    cash = 0.0
    market_val = 0.0
    fout = open(fname, 'a+')
    
    #pdb.set_trace()
    
    pool = {} #{fcode:(share, cost_amt)}
    for pos in position_data:
        posdate = pos[pos_fdate]
        fcode = pos[pos_fcode]
        qty = float(pos[pos_share])
        if ((posdate != pdate) or (qty == 0.0)): #Remove empty position
            continue
        cost_amt = float(pos[pos_cost_amt])
        pool[fcode] = (qty, cost_amt)
        #cash return
        #cash_return = cash * cf.RISK_FREE_RATE * util.year_diff(prev_fdate, fdate, cf.DAYCOUNT)
        #cash += cash_return
    cash += pool[Action_symbol.CASH][0] * 1.0
    
    #pdb.set_trace()
    
    #Aggregate cum positions, calculate share and dollar amount
    for i in range(0, len(trans_data)):
        fcode = trans_data[i][trans_fcode]
        action = trans_data[i][trans_action]
        share = float(trans_data[i][trans_share])
        trans_amt = float(trans_data[i][trans_amount])
        if action == Action_symbol.BUY: 
            share *= 1
        elif action == Action_symbol.SELL: 
            share *= -1
        cash = cash + trans_amt
        if fcode in pool:
            share += pool[fcode][0]
            trans_amt += pool[fcode][1]
        pool[fcode] = (share, trans_amt)
    pool[Action_symbol.CASH] = (cash, cash)
    
    #pdb.set_trace()
    
    #Get quote
    security = sorted(pool.keys())
    #px = [99.9 for x in security] #WST
    px = get_hist_price(fdate, security, "close")
    #wsd_data = w.wsd(security, "sec_name", fdate, fdate, "")
    #if (wsd_data.ErrorCode != 0):
    #    print 'Error in getting security name!'
    #sec_name = wsd_data.Data[0]
    
    #output daily holding positions
    for i in range(0, len(security)):
        fcode = security[i]
        share = pool[fcode][0]
        trans_amt = pool[fcode][1] #signed float, nagative number means paying out
        if fcode == Action_symbol.CASH:
            #secname = fcode
            fpx = 1.0
            cost_px = 1.0
            cost_amt = cost_px * share
            profit_pct = 0.0
            profit_amt = 0.0
            value = trans_amt
        elif (share == 0):  #Just cleanup position
            #secname = sec_name[i]
            fpx = px[i]
            cost_px = 'NULL'
            cost_amt = 'NULL'
            profit_pct = 'NULL'
            value = 0
            profit_amt = trans_amt
        else:
            #secname = sec_name[i]
            fpx = px[i]        
            cost_px = -1.0 * trans_amt / share if share > 0 else 'NULL'
            cost_amt = trans_amt if share > 0 else 'NULL'
            profit_pct = round(fpx / cost_px - 1.0, 4)
            value = fpx * share
            profit_amt = value + trans_amt
        pos_df = [Label.POSITION, fdate, portfolio_name, fcode, fpx, share, cost_px, cost_amt, profit_amt, profit_pct, value]
        #print pos_df
        fout.write("|".join([str(x) for x in pos_df]) + "\n")
        
        market_val += value

    #disgard 0 share of position
    for key in pool.keys():
        if (pool[key][0] == 0):
            pool.pop(key, None)
            
    #output
    ldf = [Label.PORTFOLIO, fdate, portfolio_name, round(market_val, 4), round(cash, 4), pool]
    fout.write("|".join([str(x) for x in ldf]) + "\n")
    fout.close()
    
    return ldf


if __name__ == '__main__':
    
    #Parameters from command line
    parser = OptionParser()
    parser.add_option("-c", "--Configfile", dest="configfpath",
                  action="store", type="string", help="Configuration file absolute path")
    parser.add_option("-s", "--Strategy", dest="strategyname",
                  action="store", type="string", help="Strategy name")
    parser.add_option("-a", "--Prevdate", dest="prevfdate",
                  action="store", type="string", help="Previous trading date")
    parser.add_option("-b", "--Currentdate", dest="currfdate",
                  action="store", type="string", help="Current trading date")
    (options, args) = parser.parse_args()
    cf = util.Configuration(options.configfpath, options.strategyname)

    #historical price
    hdf = load_hfq(cf.rawdata_file)
    #w.start()

    #merge two files
    print cf.transfile, cf.portfile
    input = []
    f1 = open(cf.transfile)
    for line in f1:
        input.append(line)
    f2 = open(cf.portfile)
    for line in f2:
        input.append(line)
    f1.close()
    f2.close()
    
    # input data is ascendingly sorted by portfolioname and then fdate
    current_pid = None
    trans_data = [] #2d arrays
    position_data = []
    cnt_err = 0 
    #f_in = open("../data/shortterm001/tmp2.txt")
    #for line in f_in:
    for line in input:
        try:
            items = line.strip().split('|')
            if len(items) < 3:
                continue
            label = int(items[0])
            fdate = items[1]
            pid = items[2]

            if current_pid == None:
                current_pid = pid
            if current_pid != pid:  #Go to next portforlio
                ldf = aggregate_position(pid, options.prevfdate, options.currfdate, position_data, trans_data, cf.portfile)
                current_pid = pid
                trans_data = []
                position_data = []

            if label == Label.POSITION and fdate == options.prevfdate:
                position_data.append(items)
            if label == Label.TRANSACTION and fdate == options.currfdate:
                trans_data.append(items)

        except ValueError:
            cnt_err += 1
            continue

    # for last day
    ldf = aggregate_position(pid, options.prevfdate, options.currfdate, position_data, trans_data, cf.portfile)
    
    #w.stop()
