# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 17:18:15 2020

@author: 西湖味精三月鲜
"""
# https://blog.csdn.net/u012735708/article/details/82460962
# https://www.itbook5.com/2019/08/11560/
# https://www.cnblogs.com/foley/p/5582358.html
# Augmented Dickey-Fuller
# https://blog.csdn.net/hal_sakai/article/details/51965657

import threading
import time
import os
import math
import pandas as pd
import sys
import logging
import platform
from imp import reload
import ibm_db
import numpy as np
import re
import xlrd
import json
import PKUPH_Calendar as calendar
import datetime
import scipy
import statsmodels.stats.weightstats as sw
import matplotlib.pyplot as plt
from matplotlib import font_manager
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

zhfont1 = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=20)

# 移动平均图
def draw_trend(timeseries, size):
    f = plt.figure(facecolor='white')
    # 对size个数据进行移动平均
    rol_mean = timeseries.rolling(window=size).mean()
    # 对size个数据移动平均的方差
    rol_std = timeseries.rolling(window=size).std()

    timeseries.plot(color='blue', label='Original')
    rol_mean.plot(color='red', label='Rolling Mean')
    rol_std.plot(color='black', label='Rolling standard deviation')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show()


def draw_ts(timeseries):
    f = plt.figure(facecolor='white')
    timeseries.plot(color='blue')
    plt.show()


# 单位根检验：ADF是一种常用的单位根检验方法，他的原假设为序列具有单位根，即非平稳，对于一个平稳的时序数据，就需要在给定的置信水平上显著，拒绝原假设。
# Dickey-Fuller test:
def teststationarity(ts):
    dftest = adfuller(ts)
    # 对上述函数求得的值进行语义描述
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    return dfoutput


from statsmodels.tsa.seasonal import seasonal_decompose


def decompose(timeseries):
    # 返回包含三个部分 trend（趋势部分） ， seasonal（季节性部分） 和residual (残留部分)
    decomposition = seasonal_decompose(timeseries, two_sided=False)

    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    plt.subplot(411)
    plt.plot(ts, label='Original')
    plt.legend(loc='best')
    plt.subplot(412)
    plt.plot(trend, label='Trend')
    plt.legend(loc='best')
    plt.subplot(413)
    plt.plot(seasonal, label='Seasonality')
    plt.legend(loc='best')
    plt.subplot(414)
    plt.plot(residual, label='Residuals')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()
    return trend, seasonal, residual


# 自相关和偏相关图，默认阶数为31阶
def draw_acf_pacf(ts, lags=31):
    f = plt.figure(facecolor='white')
    ax1 = f.add_subplot(211)
    plot_acf(ts, lags=31, ax=ax1)
    ax2 = f.add_subplot(212)
    plot_pacf(ts, lags=31, ax=ax2)
    plt.show()

def get_trend_seasonal_residual(colname):
    yearmonthlyData = pd.read_excel(r'D:\Ynby\Doc\Demo/住院数据_入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)

    yearmonthlyData['入院年月'] = [(str(eachstr)[0:4] + "-" + str(eachstr)[4:]) for eachstr in yearmonthlyData['入院年月'].values]
    yearmonthlyData.index = pd.to_datetime(yearmonthlyData['入院年月'])

    ts = yearmonthlyData[colname]
    trend, seasonal, residual = decompose(ts)
    return trend, seasonal, residual


if __name__ == "__main__":

    yearmonthlyData = pd.read_excel(r'D:\Ynby\Doc\Demo/住院数据_入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)

    yearmonthlyData['入院年月'] = [(str(eachstr)[0:4] + "-" + str(eachstr)[4:]) for eachstr in yearmonthlyData['入院年月'].values]
    yearmonthlyData.index = pd.to_datetime(yearmonthlyData['入院年月'])

    ts = yearmonthlyData['住院天数']
    draw_trend(ts, 12)
    teststationarity(ts)

    trend, seasonal, residual = decompose(ts)
    residual.dropna(inplace=True)
    draw_trend(residual, 12)
    teststationarity(residual)
    draw_acf_pacf(residual)

    ts = yearmonthlyData['死亡率']
    draw_trend(ts, 12)
    teststationarity(ts)

    trend, seasonal, residual = decompose(ts)
    residual.dropna(inplace=True)
    draw_trend(residual, 12)
    teststationarity(residual)
    draw_acf_pacf(residual)

    import itertools
    import warnings
    import statsmodels.api as sm

    # ARIMA
    # Define the p, d and q parameters to take any value between 0 and 2
    p = d = q = range(0, 2)

    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, d, q))

    # Generate all different combinations of seasonal p, q and q triplets
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

    print('Examples of parameter combinations for Seasonal ARIMA...')
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

    # warnings.filterwarnings("ignore")  # specify to ignore warning messages

    freqindex = pd.date_range(start = '2014-08-01',periods = len(yearmonthlyData['住院天数']),freq = 'MS')
    yearmonthlyData.index = freqindex
    for targetName in ['住院天数', '死亡率']:

        AICResultDf = []
        ts = yearmonthlyData[targetName]

        for param in pdq:
            for param_seasonal in seasonal_pdq:
                try:
                    mod = sm.tsa.statespace.SARIMAX(ts,
                                                    order=param,
                                                    seasonal_order=param_seasonal,
                                                    enforce_stationarity=False,
                                                    enforce_invertibility=False)

                    results = mod.fit()

                    print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
                    if len(AICResultDf) == 0:
                        AICResultDf = pd.DataFrame(np.array([str(param), str(param_seasonal), results.aic])).transpose()
                    else:
                        AICResultDf = pd.concat([AICResultDf, pd.DataFrame(
                            np.array([str(param), str(param_seasonal), results.aic])).transpose()], axis=0)

                except:
                    continue

        AICResultDf.columns = ['param', 'param_seasonal', 'AIC']
        AICResultDf['AIC'] = AICResultDf['AIC'].astype(np.float64)
        AICResultDf.sort_values('AIC', ascending=True, inplace=True)
        AICResultDf.to_excel(r'D:\Ynby\Doc\Demo/住院数据_' + targetName + '_AIC.xlsx', encoding="UTF-8", na_rep="", index=True)

    from datetime import date

    hospitalstaydays =pd.DataFrame(yearmonthlyData['住院天数'].values, index=freqindex, columns=['住院天数'])
    hospitalstaydays=hospitalstaydays["住院天数"].resample("MS").mean()#获得每个月的平均值
    param_hospitalstaydays = (1, 1, 0)
    param_seasonal_hospitalstaydays = (1, 0, 0, 12)
    mod = sm.tsa.statespace.SARIMAX(hospitalstaydays,
                                    order=param_hospitalstaydays,
                                    seasonal_order=param_seasonal_hospitalstaydays,
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results_hospitalstaydays = mod.fit()
    print(results_hospitalstaydays.summary().tables[1])
    # results_hospitalstaydays.plot_diagnostics(figsize=(15, 12))

    pred = results_hospitalstaydays.get_prediction(start=pd.to_datetime('2019-07-01'), end=pd.to_datetime('2020-07-01'), dynamic=False)
    pred_ci = pred.conf_int()
    print("pred ci:\n",pred_ci)#获得的是一个预测范围，置信区间
    print("pred mean:\n",pred.predicted_mean)#为预测的平均值

    ax=hospitalstaydays.plot(label="History")
    pred.predicted_mean.plot(ax=ax,label="Forecast",alpha=.7,color='red',linewidth=5)
    #在某个范围内进行填充
    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.2)
    ax.set_xlabel('年月', fontproperties=zhfont1)
    ax.set_ylabel('平均住院时间', fontproperties=zhfont1)
    plt.title(u'平均住院天数预测', fontproperties=zhfont1)
    plt.legend()
    plt.show()




    deathdata =pd.DataFrame(yearmonthlyData['死亡率'].values, index=freqindex, columns=['死亡率'])
    deathdata=deathdata["死亡率"].resample("MS").mean()#获得每个月的平均值
    param_death = (1, 0, 1)
    param_seasonal_death = (0, 0, 0, 12)
    mod = sm.tsa.statespace.SARIMAX(deathdata,
                                    order=param_death,
                                    seasonal_order=param_seasonal_death,
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results_deathdata = mod.fit()
    print(results_deathdata.summary().tables[1])
    # results_deathdata.plot_diagnostics(figsize=(15, 12))

    pred = results_deathdata.get_prediction(start=pd.to_datetime('2019-07-01'), end=pd.to_datetime('2020-07-01'), dynamic=False)
    pred_ci = pred.conf_int()
    print("pred ci:\n",pred_ci)#获得的是一个预测范围，置信区间
    print("pred mean:\n",pred.predicted_mean)#为预测的平均值

    ax=deathdata.plot(label="History")
    pred.predicted_mean.plot(ax=ax,label="Forecast",alpha=.7,color='red',linewidth=5)
    #在某个范围内进行填充
    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.2)
    ax.set_xlabel('年月', fontproperties=zhfont1)
    ax.set_ylabel('死亡率', fontproperties=zhfont1)
    plt.title(u'死亡率预测', fontproperties=zhfont1)
    plt.legend()
    plt.show()

