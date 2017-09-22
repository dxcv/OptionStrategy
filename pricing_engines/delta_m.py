from pricing_engines.blackcalculator import blackcalculator
from pricing_engines.svimodel import svimodel
from Utilities import utilities as util
from Utilities.hedging_utility import implied_vol_function as iv
import QuantLib as ql
import pandas as pd
import numpy as np
import math
import datetime
import os
import pickle

#hedge_date = datetime.date(2017,7,19)
#maturitydt = datetime.date(2017,9,27)
#spot = 2.702
#rf = 0.030
#params = [-0.0689813692309 , 4.57986004886 , -0.980043687933 , -0.617957974368 , 0.117468005221]
#vols = {2.2: 0.2449897447635236, 2.25: 0.22837076995826824, 2.3: 0.21949149068217633, 2.35: 0.20985304700906196, 2.4: 0.2041719266214876, 2.45: 0.20033927445461783, 2.5: 0.19807488063669001, 2.55: 0.19085764979481112, 2.6: 0.19159774017588876, 2.65: 0.1919016701828232, 2.7: 0.1934624432856883, 2.75: 0.19404949435809657}

daycounter = ql.ActualActual()
calendar = ql.China()

with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_params_calls_noZeroVol.pickle','rb') as f:
    daily_params_c = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_svi_dataset_puts_noZeroVol.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_params_puts_noZeroVol.pickle','rb') as f:
    daily_params_p = pickle.load(f)[0]


date = datetime.date(2017,7,18)
date_ql = util.to_ql_date(date)

paramset_c = daily_params_c.get(date)
paramset_p = daily_params_p.get(date)
dataset = daily_svi_dataset.get(date)
cal_vols, put_vols, maturity_dates, s, rfs = dataset
contractId = '1801'
params_c = paramset_c.get(contractId)
params_p = paramset_p.get(contractId)
maturitydt = util.get_mdate_by_contractid('m',contractId,calendar)
rf = util.get_rf_tbcurve(date_ql,daycounter,maturitydt)
ttm = daycounter.yearFraction(date_ql,maturitydt)
discount = math.exp(-rf*ttm)

# Example
strike = 2750
dS = 1.0
iscall = True

print('strike = ',strike,', option type : call')
print('='*100)
print("%10s %25s %25s %25s" % ("Spot","delta_total","delta_constant_vol ","diff"))
print('-'*100)

svi_c = svimodel(ttm,params_c)
call_delta_total = []
call_delta_cnst = []
call_diff = []
#index=['data_total','data_const']
result = pd.DataFrame()
for spot in np.arange(2400.0,3200.0,5.0):
    forward = spot / discount
    x = math.log(strike /forward , math.e)
    vol = svi_c.svi_iv_function(x)
    stdDev = vol * math.sqrt(ttm)

    black = blackcalculator(strike,forward,stdDev,discount,iscall)

    delta = black.delta(spot)
    # 隐含波动率对行权价的一阶倒数
    dSigma_dK = svi_c.calculate_dSigma_dK(strike,forward,ttm)
    # 全Delta
    delta_total = black.delta_total(spot,dSigma_dK)
    # Effective Delta
    delta_eff = svi_c.calculate_effective_delta(spot, dS,strike,discount,iscall)

    delta1 = round(delta, 4)
    delta_t1 = round(delta_total, 4)
    delta_eff1 = round(delta_eff, 4)
    call_delta_total.append(delta_total)
    call_delta_cnst.append(delta)
    call_diff.append(delta_total-delta)
    print("%10s %25s %25s %25s" % (spot,delta_t1,delta1,round(delta_total-delta,6)))
print('='*100)
result['delta_total_call'] = call_delta_total
result['delta_cnst_call'] = call_delta_cnst
result['diff_call'] = call_diff
iscall = False
print('strike = ',strike,', option type : put')
print('='*100)
print("%10s %25s %25s %25s" % ("Spot","delta_total","delta_constant_vol ","diff"))
print('-'*100)

svi_p = svimodel(ttm,params_p)
put_delta_total = []
put_delta_cnst = []
put_diff = []
for spot in np.arange(2400.0,3200.0,5.0):
    forward = spot / discount
    x = math.log(strike /forward , math.e)
    vol = svi_p.svi_iv_function(x)
    stdDev = vol * math.sqrt(ttm)

    black = blackcalculator(strike,forward,stdDev,discount,iscall)

    delta = black.delta(spot)
    # 隐含波动率对行权价的一阶倒数
    dSigma_dK = svi_p.calculate_dSigma_dK(strike,forward,ttm)
    # 全Delta
    delta_total = black.delta_total(spot,dSigma_dK)

    delta1 = round(delta, 4)
    delta_t1 = round(delta_total, 4)
    put_delta_total.append(delta_total)
    put_delta_cnst.append(delta)
    put_diff.append(delta_total-delta)
    print("%10s %25s %25s %25s" % (spot,delta_t1,delta1,round(delta_total-delta,6)))
print('='*100)
result['delta_total_put'] = put_delta_total
result['delta_cnst_put'] = put_delta_cnst
result['diff_put'] = put_diff
result.to_csv('delta_m.csv')