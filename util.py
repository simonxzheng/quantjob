#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ConfigParser
from datetime import date

class Configuration:

    def __init__(self, conf_fpath, strategy_name=""):

        if conf_fpath == None:
            self.conf_fpath = "D:\\simonxzheng\\conf\\backtest.conf"
        else:
            self.conf_fpath = conf_fpath
        cf = ConfigParser.ConfigParser()
        cf.read(self.conf_fpath)

        self.INITIAL_CASH = cf.getfloat("backtest", "initial_cash")
        self.RISK_FREE_RATE = cf.getfloat("backtest", "risk_free_rate")
        self.STAMP_DUTY_FEE_BUY = cf.getfloat("backtest", "stamp_duty_fee_buy")
        self.STAMP_DUTY_FEE_SELL = cf.getfloat("backtest", "stamp_duty_fee_sell")
        self.COMMISSION_FEE_BUY = cf.getfloat("backtest", "commission_fee_buy")
        self.COMMISSION_FEE_SELL = cf.getfloat("backtest", "commission_fee_sell")
        self.ANNUAL_TRADING_DAYS = cf.getfloat("backtest", "annual_trading_days")
        self.DAYCOUNT = cf.get("backtest", "daycount")
        
        self.BrokeID = '0000' #Mock Trading
        self.DepartID = '0' #Mock Trading
        self.mock_trd_account = cf.get('Wind', 'mock_trd_account')
        self.mock_trd_passwd = cf.get('Wind', 'mock_trd_passwd')
        self.exchange = cf.get('Wind', 'exchange')
        self.Currency = cf.get('Wind', 'Currency')

        self.rawdata_file = "D:\\sharedata\\hfq2016_wind.txt"
        data_dir = "D:\\simonxzheng\\data"
        self.signalfile = os.path.join(data_dir, strategy_name, "signal.txt")
        self.transfile = os.path.join(data_dir, strategy_name, "transaction.txt")
        self.portfile = os.path.join(data_dir, strategy_name, "portfolio.txt")
        self.valuefile = os.path.join(data_dir, strategy_name, "value.txt")        

#
# Year difference depending on day count convension.
# Day Count Convension can be 30/360, ACT/365
#
def get_trading_days(sdate, edate):
    
    td = []
    f_in = open("d:\\sharedata\\TradingDay.txt")
    for line in f_in:
        fdate = line.strip()
        if (fdate >= sdate and fdate <= edate):
            td.append(fdate)
    rtd = sorted(td)
    return rtd
 
#
# Year difference depending on day count convension.
# Day Count Convension can be 30/360, ACT/365
# input date formate 'yyyy-mm-dd' e.g. '2016-12-28'
#
def year_diff(d1, d2, daycount_convension):
	
    d1_year = d1 / 10000
    d1_month = d1 % 10000 / 100
    d1_day = d1 % 100
    d2_year = d2 / 10000
    d2_month = d2 % 10000 / 100 
    d2_day = d2 % 100
 
    ret = None
    if daycount_convension == '30/360':
        days_past = (d2_year - d1_year) * 360 + (d2_month - d1_month) * 30 + d2_day - d1_day
        ret = 1.0 * days_past / 360
    elif daycount_convension == 'ACT/365':
        date1 = date(d1_year, d1_month, d1_day)
        date2 = date(d2_year, d2_month, d2_day)
        days_past = (date2 - date1).days
        ret = 1.0 * days_past / 365

    return ret

