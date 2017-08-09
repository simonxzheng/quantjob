#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Label:

    #static data
    SIGNAL=80
    TRANSACTION=81
    POSITION=82
    PORTFOLIO=83
    MARKET_QUOTE=99
    BENCHMARK_QUOTE=100

class Action_symbol:

    #static data
    BUY='Buy'
    SELL='Sell'
    CASH='CNY'

#signal data format
sig_label=0
sig_fdate=1
sig_model=2
sig_fcode=3
sig_trd_signal=4    #Optional
sig_holding_days=5  #Optional

#transaction data format
trans_label=0
trans_fdate=1
trans_model=2
trans_time=3
trans_fcode=4
trans_action=5
trans_price=6
trans_share=7
trans_stamp_duty=8
trans_commission=9
trans_amount=10

#position data format
pos_label=0
pos_fdate=1
pos_model=2
pos_fcode=3
pos_latest_px=4
pos_share=5
pos_cost_px=6    #unsigned number
pos_cost_amt=7   #signed number, negative number means payout
pos_profit_amt=8 #floating amt
pos_profit_pct=9
pos_market_value=10

#Portfolio data format                                                                                                                                
port_label=0
port_fdate=1 
port_model=2                                                                                                                                                                                                                                                    
port_market_value=3                                                                                                                                   
port_cash=4                                                                                                                             
port_pool=5
port_bucket=6 #optional
