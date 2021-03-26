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
outfolder = r'D:\Ynby\Doc\Demo\按出院时间维度_出入院时间'

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
    yearmonthlyData = pd.read_excel(outfolder+r'/住院数据_入院年月统计_出入院时间.xlsx', encoding="UTF-8", na_rep="", index=True)

    yearmonthlyData['入院年月'] = [(str(eachstr)[0:4] + "-" + str(eachstr)[4:]) for eachstr in yearmonthlyData['入院年月'].values]
    yearmonthlyData.index = pd.to_datetime(yearmonthlyData['入院年月'])

    ts = yearmonthlyData[colname]
    trend, seasonal, residual = decompose(ts)
    return trend, seasonal, residual



if __name__ == "__main__":

    yearmonthlyData = pd.read_excel(outfolder+r'/住院数据_入院年月统计_出入院时间.xlsx', encoding="UTF-8", na_rep="", index=True)

    yearmonthlyData['入院年月'] = [(str(eachstr)[0:4] + "-" + str(eachstr)[4:]) for eachstr in yearmonthlyData['入院年月'].values]
    yearmonthlyData.index = pd.to_datetime(yearmonthlyData['入院年月'])

    ts = yearmonthlyData['住院天数_出入院时间']
    draw_trend(ts, 12)
    teststationarity(ts)

    trend, seasonal, residual = decompose(ts)
    residual.dropna(inplace=True)
    draw_trend(residual, 12)
    stationarity = teststationarity(residual)
    draw_acf_pacf(residual)

    trend.to_excel(outfolder+r'/住院数据_住院天数_出入院时间_趋势.xlsx', encoding="UTF-8", na_rep="", index=True)
    seasonal.to_excel(outfolder+r'/住院数据_住院天数_出入院时间_周期.xlsx', encoding="UTF-8", na_rep="", index=True)
    residual.to_excel(outfolder+r'/住院数据_住院天数_出入院时间_残差.xlsx', encoding="UTF-8", na_rep="", index=True)
    stationarity.to_excel(outfolder+r'/住院数据_住院天数_出入院时间_单位根检验ADF检验.xlsx', encoding="UTF-8", na_rep="", index=True)

    ts = yearmonthlyData['死亡率']
    draw_trend(ts, 12)
    teststationarity(ts)

    trend, seasonal, residual = decompose(ts)
    residual.dropna(inplace=True)
    draw_trend(residual, 12)
    stationarity = teststationarity(residual)
    draw_acf_pacf(residual)

    trend.to_excel(outfolder+r'/住院数据_死亡率_趋势.xlsx', encoding="UTF-8", na_rep="", index=True)
    seasonal.to_excel(outfolder+r'/住院数据_死亡率_周期.xlsx', encoding="UTF-8", na_rep="", index=True)
    residual.to_excel(outfolder+r'/住院数据_死亡率_残差.xlsx', encoding="UTF-8", na_rep="", index=True)
    stationarity.to_excel(outfolder+r'/住院数据_死亡率_单位根检验ADF检验.xlsx', encoding="UTF-8", na_rep="", index=True)

    ts = yearmonthlyData['患者编号']
    draw_trend(ts, 12)
    teststationarity(ts)

    trend, seasonal, residual = decompose(ts)
    residual.dropna(inplace=True)
    draw_trend(residual, 12)
    stationarity = teststationarity(residual)
    draw_acf_pacf(residual)

    trend.to_excel(outfolder+r'/住院数据_住院人数_趋势.xlsx', encoding="UTF-8", na_rep="", index=True)
    seasonal.to_excel(outfolder+r'/住院数据_住院人数_周期.xlsx', encoding="UTF-8", na_rep="", index=True)
    residual.to_excel(outfolder+r'/住院数据_住院人数_残差.xlsx', encoding="UTF-8", na_rep="", index=True)
    stationarity.to_excel(outfolder+r'/住院数据_住院人数_单位根检验ADF检验.xlsx', encoding="UTF-8", na_rep="", index=True)

