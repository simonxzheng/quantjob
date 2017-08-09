# -*- coding:utf-8 -*-
#Python 2.7
from WindPy import w
import datetime
import sys
import os
from optparse import OptionParser
import time
import math
import pdb
import util
from dataformat import *
import pandas as pd

#Global variable
hdf = []

#
# Wind API wrapper
#
def logon(cf):
    #LogonID = w.tlogon(cf.BrokeID, cf.DepartID, cf.mock_trd_account, cf.mock_trd_passwd, cf.exchange)
    #LogonID = w.tlogon('0000','0', 'W100232803301', 'ABC123', 'SHSZ')
    LogonID = w.tlogon('0000','0', '1860104366801', '111111', 'SHSZ')
    if (LogonID.ErrorCode != 0):
        print "Error in logon account! haha "
        return None
    
    return LogonID.Data[0]

def logout(logonid):
    LogoutID = w.tlogout(logonid)
    if (LogoutID.ErrorCode != 0):
        print "Error in logout account!"
        return -1
    return 0

def query_login():
    LogID = w.tquery('LogonID')
    if (LogID.ErrorCode != 0):
        print "Error in query!"
        return None
    return LogID.Data[1]
    
#下单
def put_order(logonid):
    code = ['603300.SH', '000001.SZ']
    price = w.wsq(code,'rt_last').Data[0]
    tradeside = ['buy', 'buy']
    quantity = [100, 100] 
    torder_data = w.torder(code, 'buy', price, 100, logonid=logonid)
    if (torder_data.ErrorCode != 0):
        print "Error in making orders!"
        return -1
        
    print torder_data
    return 0;

#查询资金    
def query_fund(logonID):
    qrycode = 'Capital'
    query_data = w.tquery(qrycode, logonid=logonID)
    print query_data
    
    return 0

#查询仓位
def query_position(logonID):
    qrycode = 'Position'
    query_data = w.tquery(qrycode, logonid=logonID, showfields='securitycode,Profit,securityBalance')
    print query_data

    
#查询委托
def query_order(logonID):
    qrycode = 'Order'
    query_data = w.tquery(qrycode, logonid=logonID)
    print query_data
    
    return
    
#查询成交
def query_trade(logonID):
    qrycode = 'Trade'
    query_data = w.tquery(qrycode, logonid=logonID)
    print query_data

    return
    
# 撤销委托
def cancel_order(logonID):
    qrycode = 'Order'
    #cancel_data = w.tcancel(Data3(:,1), logonid, Data1{2,1});
    return 

    
#实时下单
def put_real_order(pmsName, fdate, tradeside, security, quantity):

    logonID = logon(cf)
    price = w.wsq(security,'rt_last').Data[0]
    ordertype = ['B5TC' for x in security] #最优五档剩余撤销
    hedgetype = ['SPEC' for x in security]
    torder_data = w.torder(security, tradeside, price, quantity, ordertype, hedgetype, logonid=logonID)
    if (torder_data.ErrorCode != 0):
        print "Error in download portfolio details!"
        return -1
    print torder_data
    #w.tlogout(logid)

    return 0;


def amount_to_quantity(price, amount):

    quantity = []
    for i in range(0, len(price)):
        px = price[i]
        amt = amount[i]
        qty = amt * (1-cf.STAMP_DUTY_FEE_BUY - cf.COMMISSION_FEE_BUY) / px
        qty = math.floor(qty / 100) * 100
        quantity.append(qty)
    
    return quantity

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


#历史收盘价下单
#quantity have to be positive int
#
def put_hist_order(pid, fdate, tradeside, tradetime, security, quantity, price):

    ldf = []
    for i in range(0, len(security)):
        fcode = security[i]
        action = tradeside[i]
        trans_time = tradetime[i]
        qty = quantity[i]
        if (qty <= 0):
            continue
        
        if (fcode == Action_symbol.CASH):
            px = 1.0
        elif (math.isnan(price[i]) == True):
            continue
        else:
            px = price[i]
        amount = 0.0
        stamp_duty = 0.0
        commission = 0.0
        trans_amt = 0.0
        amount = px * qty
        
        if (fcode == Action_symbol.CASH):
            trans_amt = amount 
        elif (action == Action_symbol.BUY):                                                                                                              
            stamp_duty = amount * cf.STAMP_DUTY_FEE_BUY                                                                                               
            commission = amount * cf.COMMISSION_FEE_BUY                                                                                               
            trans_amt = -1.0 * amount - commission - stamp_duty                                                                                              
        elif (action == Action_symbol.SELL):     
            stamp_duty = amount * cf.STAMP_DUTY_FEE_SELL                                                                                              
            commission = amount * cf.COMMISSION_FEE_SELL                                                                                              
            trans_amt = amount - commission - stamp_duty                                                                                       
                              
        #output format                              
        ldf.append([Label.TRANSACTION, fdate, pid, trans_time, fcode, action, px, qty, stamp_duty, commission, trans_amt])
    
    return ldf;    

#
# Strategy specified function.
# adjust positions for specifiy fdate
#
def do_transaction(pid, pdate, fdate, positions, signals, fname):
    
    sell_df = []
    buy_df = []
    
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    hr = time.strftime('%H%M%S',time.localtime(time.time()))
    
    #Step 0: count cash amount
    total_cash = 0.0
    for pos in positions:
        fcode = pos[pos_fcode]
        qty = float(pos[pos_share])
        if fcode == Action_symbol.CASH:
            total_cash = qty * 1.0
            break

    #Step1: sell prevailing positions by open or close price
    tradeside = []
    tradetime = []
    security = []
    quantity = []
    price = []
    for pos in positions:
        posdate = pos[pos_fdate]
        fcode = pos[pos_fcode]
        qty = float(pos[pos_share])
        if ((posdate != pdate) or (qty == 0.0)): #Remove empty position
            continue
        if fcode != Action_symbol.CASH:
            tradeside.append(Action_symbol.SELL)
            security.append(fcode)
            quantity.append(qty)
            tradetime.append("09:00:00")
            price.append(0.0)

    if (today == fdate and int(hr) >= 91500 and int(hr) <= 150000):
        sell_df = put_real_order(pid, fdate, tradeside, security, quantity)
    else:
        prev_open_price = get_hist_price(pdate, security, "open")
        open_price = get_hist_price(fdate, security, "open")
        close_price = get_hist_price(fdate, security, "close")
        susp_days = get_hist_price(fdate, security, "susp_days")
        #pdb.set_trace()
        #unable to sell in case of suspending
        for i in range(0, len(security)):
            if (susp_days[i] > 0):
                quantity[i] = 0
                continue
            if (open_price[i] / prev_open_price[i] - 1.0 > 0.09):
                tradetime[i] = "09:30:00"
                price[i] = open_price[i]
                ldf = put_hist_order(pid, fdate, [tradeside[i]], [tradetime[i]], [security[i]], [quantity[i]], [price[i]])
                sell_df = sell_df + ldf
                if len(ldf) > 0:
                    total_cash += ldf[0][trans_amount]
            else:
                tradetime[i] = "15:00:00"
                price[i] = close_price[i]
                ldf = put_hist_order(pid, fdate, [tradeside[i]], [tradetime[i]], [security[i]], [quantity[i]], [price[i]])
                sell_df = sell_df + ldf

    #Step 2: buy orders, pick yesterday signal and then buy by open price, adjust position by equal weights
    yesterday_signals = []
    for sig in signals:
        if (sig[sig_fdate] == pdate):
            yesterday_signals.append(sig)
    tradeside = []
    security = []
    amount = []
    for sig in yesterday_signals:
        fcode = sig[sig_fcode]
        amt = total_cash / len(yesterday_signals)
        tradeside.append(Action_symbol.BUY)
        security.append(fcode)
        amount.append(amt)
    
    if (today == fdate and int(hr) >= 91500 and int(hr) <= 150000):
        #price = get_real_price(security, fdate)
        #quantity = amount_to_quantity(price, amount)
        buy_df = put_real_order(pid, fdate, tradeside, security, quantity)
    else:
        open_price = get_hist_price(fdate, security, "open")
        tradetime = ["09:30:00"] * len(security)
        pre_close_price = get_hist_price(fdate, security, "pre_close")
        quantity = amount_to_quantity(open_price, amount)
        #unable to buy in case of maxup
        for i in range(0, len(security)):
            open_chg = open_price[i] / pre_close_price[i] - 1.0
            if (open_chg > -0.02 and open_chg < 0.015) or (open_chg > 0.05 and open_chg < 0.099):
                quantity[i] = quantity[i]
            else:
                quantity[i] = 0
        buy_df = put_hist_order(pid, fdate, tradeside, tradetime, security, quantity, open_price)

    #output
    fout = open(fname, 'a+')
    for ldf in sell_df:
        fout.write("|".join([str(x) for x in ldf]) + "\n")
    for ldf in buy_df:
        fout.write("|".join([str(x) for x in ldf]) + "\n")
    
    return (sell_df, buy_df)

    
if __name__ == '__main__':

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
        
    #w.start();

    #merge two files
    input = []
    f1 = open(cf.signalfile)
    for line in f1:
        input.append(line)
    f2 = open(cf.portfile)
    for line in f2:
        input.append(line)
    f1.close()
    f2.close()

    # input data is ascendingly sorted by portfolioname and then fdate
    current_pid = None
    positions = []
    signals = []
    cnt_err = 0
    for line in input:
        try:
            #pdb.set_trace()
            
            items = line.strip().split('|')
            if len(items) < 3:
                continue
            label = int(items[0])
            fdate = items[1]
            pid = items[2]
            
            if current_pid == None:
                current_pid = pid
            if current_pid != pid:
                (sell_df, buy_df) = do_transaction(current_pid, options.prevfdate, options.currfdate, positions, signals, cf.transfile)
                signals = []
                positions = []
                current_pid = pid
            
            if label == Label.POSITION and fdate == options.prevfdate:
                positions.append(items)
            elif label == Label.SIGNAL and fdate in [options.prevfdate, options.currfdate]:
                signals.append(items)

        except ValueError:
            cnt_err += 1
            continue

    #for last line
    (sell_df, buy_df) = do_transaction(current_pid, options.prevfdate, options.currfdate, positions, signals, cf.transfile)

    #w.stop();
 