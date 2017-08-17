import operator
import matplotlib.pyplot as plt
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
import svi_read_data as raw_data
import QuantLib as ql
import plot_util as pu
from WindPy import w
import numpy as np


def get_iv_plot_data(cal_vols_data, put_vols_data):
    call_volatilities_op = {}
    put_volatilities_op = {}
    strikes_op = {}
    ql.Settings.instance().evaluationDate = evalDate
    for idx_month,call_vol_dict in enumerate(cal_vols_data):
        put_vol_dict = put_vols_data[idx_month]
        call_volatilities = []
        put_volatilities = []
        strikes = []
        call_sorted = sorted(call_vol_dict.items(), key=operator.itemgetter(0))
        call_vol_dict_sorted = dict(call_sorted)
        put_sorted = sorted(put_vol_dict.items(), key=operator.itemgetter(0))
        put_vol_dict_sorted = dict(put_sorted)

        for k in call_vol_dict_sorted.keys():
            strikes.append(k)
            call_volatilities.append(call_vol_dict_sorted.get(k)[0])
            put_volatilities.append(put_vol_dict_sorted.get(k)[0])

        strikes_op.update({idx_month:strikes})
        call_volatilities_op.update({idx_month:call_volatilities})
        put_volatilities_op.update({idx_month:put_volatilities})
    return strikes_op,call_volatilities_op,put_volatilities_op
w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(19,7,2017)
begDate  = evalDate

# Underlying close prices
spotprice_dic = raw_data.get_underlying_ts()


curve = svi_data.get_curve_treasury_bond(evalDate, daycounter)

#rf_avg_months =  calculate_PCParity_riskFreeRate(evalDate,daycounter,calendar)

cal_vols_data, put_vols_data = svi_data.get_call_put_impliedVols_strikes(evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
strikes_op,call_volatilities_op_m,put_volatilities_op_m =get_iv_plot_data(cal_vols_data, put_vols_data)


i = 2
strikes = strikes_op.get(i)
callvols = call_volatilities_op_m.get(i)
putvols = put_volatilities_op_m.get(i)

mark = "o"
line = pu.l3
print(putvols[-2:len(putvols)])
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})

f, axarr = plt.subplots()
axarr.plot(strikes, callvols,color = pu.c1,marker = "^",linestyle = pu.l1,linewidth = 2,label="认购期权隐含波动率")
axarr.set_xlabel('行权价')
axarr.legend()

f1, axarr1 = plt.subplots()
axarr1.plot(strikes, putvols,color = pu.c1,marker = "^",linestyle = pu.l1,linewidth = 2,label="认沽期权隐含波动率")
axarr1.set_xlabel('行权价')
axarr1.legend()


axarr.spines['right'].set_visible(False)
axarr.spines['top'].set_visible(False)
axarr.yaxis.set_ticks_position('left')
axarr.xaxis.set_ticks_position('bottom')
axarr1.spines['right'].set_visible(False)
axarr1.spines['top'].set_visible(False)
axarr1.yaxis.set_ticks_position('left')
axarr1.xaxis.set_ticks_position('bottom')

f.savefig('implied_vols_call ,'+ str(evalDate) +'.png', dpi=300, format='png')
f1.savefig('implied_vols_put ,'+ str(evalDate) +'.png', dpi=300, format='png')


plt.draw()
plt.show()

