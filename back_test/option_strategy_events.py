import pandas as pd
import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from scipy.optimize import minimize
import scipy.optimize as optimize
from matplotlib import pyplot as plt
import numpy as np
import math

class option_strategy_events(object):

    def __init__(self,df_events,df_vix):
        self.df_events = df_events
        self.df_vix = df_vix
        self.dt_list = sorted(df_vix['dt_date'].unique())
        self.event_ids = list(df_events['id_event'])
        self.nbr_events = len(self.event_ids)
        self.event_id = self.event_ids[0]
        self.x = []
        self.y = []
        self.y_1 = []

    # Analyze Event Influence Significance
    def add_nbr_days_from_events(self):
        for (idx_e,r_e) in self.df_events.iterrows():
            dt_event = r_e['dt_first_trading']
            id_event = r_e['id_event']
            self.df_vix[id_event] = self.calculate_nbr_days(self.df_vix['dt_date'], dt_event)

    def calculate_nbr_days(self,dt_list,dt_event):
        nbr_days = []
        for dt in dt_list:
            idx_dt = self.dt_list.index(dt)
            idx_evt = self.dt_list.index(dt_event)
            nbr = idx_dt-idx_evt
            nbr_days.append(nbr)
        return nbr_days

    def normal_distribution(self,dt,mu,s):
        # mu = max(1e-10,mu)
        # s = max(1e-10,s)
        return math.exp(-(dt-mu)**2/(2*s**2))/(s*math.sqrt(2*math.pi))

    def lognormal_distribution(self,dt,mu,s):
        # mu = max(1e-10,mu)
        # s = max(1e-10,s)
        return math.exp(-(dt-mu)**2/(2*s**2))/(math.log(s,math.e)*math.sqrt(2*math.pi))


    # def func_derm(self,params):
    #     a,d,beta,mu,sigma = params
    #     obj = 0
    #     for (idx_vix,r_vix) in self.df_vix.iterrows():
    #         if idx_vix == 0 : continue
    #         norm = 0
    #         dt = r_vix[self.event_id]
    #         if dt > 30 or dt < -30: continue
    #         norm += beta * self.normal_distribution(dt, mu, sigma)
    #         y_t = r_vix['amt_close']
    #         y_t1 = self.df_vix.loc[idx_vix-1,'amt_close']
    #         obj_t = - y_t + a + d*y_t1 + norm
    #         obj += obj_t
    #         self.x.append(dt)
    #         self.y.append(y_t)
    #         self.y_1.append(y_t1)
    #     # print(params)
    #     return obj

    # def optimization_minimize(self):
    #     init_params = np.ones(5)
    #     bnds = ((1e-3,50), (-1,1), (None,None),(1e-3,30),(1e-3,100))
    #     res = minimize(abs(self.func_derm), init_params, method='L-BFGS-B', bounds =bnds,tol=1e-3)
    #     # res = minimize(self.func_derm, init_params, method='Nelder-Mead',tol=1e-3)
    #     # res = minimize(self.func_derm, init_params, method='SLSQP')
    #     return res

    def nerm_residuals(self,params):
        a,d,beta,mu,sigma = params
        squred_e = 0
        for (idx_vix,r_vix) in self.df_vix.iterrows():
            if idx_vix == 0 : continue
            norm = 0
            dt = r_vix[self.event_id]
            if dt > 60 or dt < -60: continue
            norm += beta * self.normal_distribution(dt, mu, sigma)
            y_t = r_vix['amt_close']
            y_t1 = self.df_vix.loc[idx_vix-1,'amt_close']
            obj_t = - y_t + a + d*y_t1 + norm
            # obj_t = - y_t + a + norm
            squred_e += obj_t**2
            if dt not in self.x:
                self.x.append(dt)
                self.y.append(y_t)
                self.y_1.append(y_t1)
        # print(params)
        return squred_e

    def lnerm_residuals(self,params):
        a,d,beta,mu,sigma = params
        squred_e = 0
        for (idx_vix,r_vix) in self.df_vix.iterrows():
            if idx_vix == 0 : continue
            norm = 0
            dt = r_vix[self.event_id]
            if dt > 60 or dt < -60: continue
            norm += beta * self.lognormal_distribution(dt, mu, sigma)
            y_t = r_vix['amt_close']
            y_t1 = self.df_vix.loc[idx_vix-1,'amt_close']
            obj_t = - y_t + a + d*y_t1 + norm
            # obj_t = - y_t + a + norm
            squred_e += obj_t**2
            if dt not in self.x:
                self.x.append(dt)
                self.y.append(y_t)
                self.y_1.append(y_t1)
        # print(params)
        return squred_e

    def optimization_ols(self):
        init_params = np.ones(5)
        # init_params = np.ones(4)
        bnds = ((1e-3, 50), (-1, 1), (None, None), (1e-3, 30), (1e-3, 100))
        # bnds = ((1e-3, 50), (None, None), (1e-3, 30), (1e-3, 100))
        # res = minimize(self.nerm_residuals, init_params, method='L-BFGS-B', bounds=bnds, tol=1e-3)
        res = minimize(self.lnerm_residuals, init_params, method='L-BFGS-B', bounds=bnds, tol=1e-3)
        # res = minimize(self.func_derm, init_params, method='Nelder-Mead',tol=1e-3)
        # res = minimize(self.func_derm, init_params, method='SLSQP')
        return res

    def event_analysis(self):
        for (idx_e, r_e) in self.df_events.iterrows():
            self.x.clear()
            self.y.clear()
            self.y_1.clear()
            try:
                self.event_id = r_e['id_event']
                print(r_e)
                # res = self.optimization_minimize()
                res = self.optimization_ols()
                x = self.x
                y = self.y
                print('='*50)
                print(self.event_id)
                print('-'*50)
                print(res.x)
                print(res.success)
                print(res.message)
                a, d, beta, mu, sigma = res.x
                # a, beta, mu, sigma = res.x
                res_y = []
                res_norm = []
                for (i,xi) in enumerate(x):
                    yi = a + d*self.y_1[i] + beta*self.normal_distribution(xi,mu,sigma)
                    # yi = a + beta*self.normal_distribution(xi,mu,sigma)

                    res_y.append(yi)
                x_norm = np.arange(-10,30,1)
                for xj in x_norm:
                    res_norm.append(beta * self.normal_distribution(xj, mu, sigma))
                plt.figure(idx_e)
                plt.scatter(x, y,label='data')
                plt.plot(x, res_y,label='regress',color='r')
                plt.legend()
                plt.figure(idx_e+1)
                plt.plot(x_norm, res_norm,label='regress 2',color='y')
                plt.legend()
                plt.show()
                plt.clf()
            except:
                pass


    def nerm_residuals_fun(self,params):
        a = params[0]
        d = params[1]
        beta_list = params[2:2+self.nbr_events]
        mu_list = params[2+self.nbr_events:2+self.nbr_events*2]
        sigma_list = params[2+self.nbr_events*2:]
        squared_e = 0
        for (idx_vix,r_vix) in self.df_vix.iterrows():
            if idx_vix == 0 : continue
            norm = 0
            for (idx_e, r_e) in self.df_events.iterrows():
                event_id = r_e['id_event']
                dt = r_vix[event_id]
                if dt >30 or dt< -30 : continue
                norm += beta_list[idx_e] * self.normal_distribution(dt,mu_list[idx_e], sigma_list[idx_e])
            y_t = r_vix['amt_close']
            y_t1 = self.df_vix.loc[idx_vix-1,'amt_close']
            obj_t = - y_t + a + d*y_t1 + norm
            squared_e += obj_t**2
            date = r_vix['dt_date']
        print(params)
        return squared_e



    def optimize_events(self):
        init_params = np.ones(3*self.nbr_events+2)
        res = minimize(self.nerm_residuals_fun, init_params, method='L-BFGS-B',tol=1e-3)
        params = res.x
        res_y = []
        res_norm = []
        x_norm = []
        events = []
        x = []
        y = []
        a = params[0]
        d = params[1]
        beta_list = params[2:2+self.nbr_events]
        mu_list = params[2+self.nbr_events:2+self.nbr_events*2]
        sigma_list = params[2+self.nbr_events*2:]
        tss = 0

        ess = 0 # explained sum of squared errors
        for (idx_vix,r_vix) in self.df_vix.iterrows():
            if idx_vix == 0 : continue
            norm = 0
            date = r_vix['dt_date']
            for (idx_e, r_e) in self.df_events.iterrows():
                event_id = r_e['id_event']
                dt = r_vix[event_id]
                # if dt >30 or dt< -30 : continue
                if dt == 0:
                    x_norm.append(date)
                    events.append(2)
                norm += beta_list[idx_e] * self.normal_distribution(dt,mu_list[idx_e], sigma_list[idx_e])
            y_t = r_vix['amt_close']
            y_t1 = self.df_vix.loc[idx_vix-1,'amt_close']
            res_y.append(a + d*y_t1 + norm)
            x.append(date)
            y.append(y_t)
            res_norm.append(norm)
        y_mean = np.mean(y)
        for res_yi in res_y:
            ess += (res_yi-y_mean)**2
        for yi in y:
            tss += (yi - y_mean) ** 2
        rss = tss - ess  # residual sum of squared errors
        print('=' * 100)
        df_res = pd.DataFrame()
        cov = res.hess_inv.todense()
        print('cov : ',cov)
        cov_ii = np.diag(cov)
        beta_cov = cov_ii[2:2+self.nbr_events]
        mu_cov = cov_ii[2+self.nbr_events:2+self.nbr_events*2]
        sigma_cov = cov_ii[2+self.nbr_events*2:]
        df = len(self.dt_list) - self.nbr_events*3 -3
        print('df : ',df)
        for (idx_e, r_e) in self.df_events.iterrows():
            event_id = r_e['id_event']
            print(event_id)
            b = beta_list[idx_e]
            mu = mu_list[idx_e]
            s = sigma_list[idx_e]
            #SE(Pi) = sqrt[(SS / DF) * Cov(i, i)]
            t_b = b/np.sqrt(beta_cov[idx_e]*rss/df)
            t_mu = mu/np.sqrt(mu_cov[idx_e]*rss/df)
            t_s = s/np.sqrt(sigma_cov[idx_e]*rss/df)
            # t_b = b/np.sqrt(beta_cov[idx_e])
            # t_mu = mu/np.sqrt(mu_cov[idx_e])
            # t_s = s/np.sqrt(sigma_cov[idx_e])
            print('beta : ',b, ' ',t_b)
            print('mu : ',mu, ' ',t_mu)
            print('sigma : ',s, ' ',t_s)
            r = pd.DataFrame(
                data={'1-id_event': [event_id], '2-name_event': [r_e['name_event']],
                      '3-beta': [beta_list[idx_e]],
                      '4-mu': [mu_list[idx_e]], '5-sigma': [sigma_list[idx_e]],
                      '6-a': [a], '7-d': [d],'8-ttest_beta':[t_b],'9-ttest_mu':[t_mu],
                      '10-ttest':[t_s]},
                index=[event_id])
            df_res = df_res.append(r)
        print('TSS : ',tss)
        print('RSS : ',rss)
        print('R square : ',ess/tss)
        r = pd.DataFrame(
            data={'1-TSS': [tss], '2-ESS': [ess], '3-R square': [ess/tss]}, index=[1111])
        df_res = df_res.append(r)
        df_res.to_csv('../save_results/drem_regression_results.csv')
        plt.figure(1)
        plt.scatter(x, y, label='data')
        plt.plot(x, res_y, label='regress',color='r')
        plt.legend()
        plt.figure(2)
        plt.plot(x, res_norm, label='nerm')
        plt.bar(x_norm, events, label='event',color = 'r')
        plt.legend()
        plt.show()
        return res




engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata?charset=utf8mb4', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
events = Table('events', metadata, autoload=True)
indexes = Table('indexes_mktdata', metadata, autoload=True)
query_events = sess.query(events).filter(events.c.dt_first_trading > '2015-3-1')\
                                .filter(events.c.dt_first_trading < '2018-3-1')\
                                .filter(events.c.flag_impact == 1)
query_vix = sess.query(indexes.c.dt_date,indexes.c.id_instrument,indexes.c.amt_close)\
    .filter(indexes.c.id_instrument == 'index_cvix')\
    .filter(indexes.c.dt_date > '2015-3-1')\
    .filter(indexes.c.dt_date < '2018-3-1')

df_events = pd.read_sql(query_events.statement,query_events.session.bind)
df_vix = pd.read_sql(query_vix.statement,query_vix.session.bind)

s = option_strategy_events(df_events,df_vix)
s.add_nbr_days_from_events()
# s.event_analysis()
res = s.optimize_events()
