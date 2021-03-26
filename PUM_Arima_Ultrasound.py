#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
https://www.howtoing.com/a-guide-to-time-series-forecasting-with-arima-in-python-3/
http://www.statsmodels.org/stable/datasets/index.html
"""

import warnings
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import datetime
from matplotlib import font_manager
import xlrd
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

zhfont1 = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=40)


'''
1-Load Data

Most sm.datasets hold convenient representations of the data in the attributes endog and exog.
If the dataset does not have a clear interpretation of what should be an endog and exog, 
then you can always access the data or raw_data attributes.

https://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html
http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.resample.html

# resample('MS') groups the data in buckets by start of the month,
# after that we got only one value for each month that is the mean of the month

# fillna() fills NA/NaN values with specified method
# 'bfill' method use Next valid observation to fill gap
# If the value for June is NaN while that for July is not, we adopt the same value
# as in July for that in June
'''

'''
2-ARIMA Parameter Seletion

ARIMA(p,d,q)(P,D,Q)s
non-seasonal parameters: p,d,q
seasonal parameters: P,D,Q
s: period of time series, s=12 for annual period

Grid Search to find the best combination of parameters
Use AIC value to judge models, choose the parameter combination whose
AIC value is the smallest

https://docs.python.org/3/library/itertools.html
http://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html
'''

parent_folder = r'D:\Ynby\Doc\协和Demo'

# Define the p, d and q parameters to take any value between 0 and 2
p = d = q = range(0, 2)

# Generate all different combinations of p, q and q triplets
pdq = list(itertools.product(p, d, q))

filename = parent_folder + r'/超声刀实验数据9-27_OnlyData.xlsx'
b = xlrd.open_workbook(filename)

for eachMode in ['Forward:', 'Backward:', 'Downward:']:
    for targetName in ['X', 'Y', 'Z', "All"]:
        allstationarity = []
        for sheetId in range(len(b.sheets())):
            sheet1 = pd.read_excel(filename, sheetname=b.sheets()[sheetId].name, header=None, encoding="UTF-8", na_rep="", index=True)
            sheet1.columns = ['No', 'Mode', 'X', 'Y', 'Z', "All"]
            sheet1 = sheet1[sheet1['Mode'] == eachMode]
            NoLength = sheet1['No'].value_counts()

            period = int(np.median(NoLength.values))

            sheet1.index = pd.date_range('1900-01-01', periods=len(sheet1), freq='D')

            # Generate all different combinations of seasonal p, q and q triplets
            seasonal_pdq = [(x[0], x[1], x[2], period) for x in pdq]

            y = sheet1[targetName]

            warnings.filterwarnings("ignore") # specify to ignore warning messages

            AICDf = []
            for param in pdq:
                for param_seasonal in seasonal_pdq:
                    try:
                        mod = sm.tsa.statespace.SARIMAX(y,
                                                        order=param,
                                                        seasonal_order=param_seasonal,
                                                        enforce_stationarity=False,
                                                        enforce_invertibility=False)

                        results = mod.fit()

                        print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
                        if len(AICDf) == 0:
                            AICDf = pd.DataFrame([str(param), str(param_seasonal), results.aic]).transpose()
                        else:
                            AICDf = pd.concat([AICDf, pd.DataFrame([str(param), str(param_seasonal), results.aic]).transpose()], axis=0)
                    except:
                        continue

            AICDf.columns = ['param', 'param_seasonal', 'AIC']
            AICDf.sort_values(by='AIC', ascending=True, inplace=True)
            AICDf.head(1)

            AICDf.to_excel(parent_folder + r'/Result/' + eachMode.replace(":", "_") + targetName+ '_超声刀_Sample' + b.sheets()[sheetId].name +r'_ARIMA参数_AIC.xlsx', encoding="UTF-8", na_rep="", index=True)

'''
3-Optimal Model Analysis

Use the best parameter combination to construct ARIMA model
Here we use ARIMA(1,1,1)(1,1,1)12 
the output coef represents the importance of each feature

mod.fit() returnType: MLEResults 
http://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.mlemodel.MLEResults.html#statsmodels.tsa.statespace.mlemodel.MLEResults

Use plot_diagnostics() to check if parameters are against the model hypothesis
model residuals must not be correlated
'''


sheetId=0
eachMode = 'Forward:'
sheet1 = pd.read_excel(filename, sheetname=b.sheets()[sheetId].name, header=None, encoding="UTF-8", na_rep="", index=True)
sheet1.columns = ['No', 'Mode', 'X', 'Y', 'Z', "All"]
sheet1 = sheet1[sheet1['Mode'] == eachMode]

lastNo = sheet1['No'].iloc[-1]
# noList = ['No.5', 'No.6', 'No.7', 'No.8', 'No.9']
last5NoList = [eachstr for eachstr in np.unique(sheet1['No']) if eachstr != lastNo]
last5NoList = last5NoList[-5:]
reallast5NoList = last5NoList[-5:] + [lastNo]
last5layers = sheet1.iloc[[rowId for rowId in range(len(sheet1)) if sheet1['No'].iloc[rowId] in last5NoList], :]
reallast5layers = sheet1.iloc[[rowId for rowId in range(len(sheet1)) if sheet1['No'].iloc[rowId] in reallast5NoList], :]
last5NoLength = last5layers['No'].value_counts()
last5period = int(np.min(last5NoLength))

for targetName in ['X', 'Y', 'Z', "All"]:
    # y = last5layers[targetName]

    allDf = []
    for eachNo in last5NoList:
        eachDf = last5layers[last5layers['No'] == eachNo]
        dropPointNum = len(eachDf) - last5period
        if len(eachDf) > last5period:
            np.random.seed(1234)
            eachDf = eachDf.iloc[[rowId for rowId in range(len(eachDf)) if rowId not in np.random.randint(5, len(eachDf)-5, [dropPointNum])], :]
            # eachDf = eachDf.iloc[:last5period, :]
        if len(allDf) == 0:
            allDf = eachDf
        else:
            allDf = pd.concat([allDf, eachDf], axis=0)

    allDf.index = pd.date_range('1900-01-01', periods=len(allDf), freq='D')

    y = allDf[targetName]
    mod = sm.tsa.statespace.SARIMAX(y,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 1, 0, last5period),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results = mod.fit()
    plt.figure(figsize=(16, 8))
    plt.title('超声刀'+targetName, fontproperties=zhfont1)
    plt.plot(y, label='History')
    plt.plot(results.forecast(last5period), label='SARIMA')
    plt.legend(loc='best')
    plt.xticks([y.index[0], y.index[0+last5period], y.index[0+2*last5period], y.index[0+3*last5period], y.index[0+4*last5period], y.index[0+4*last5period] + (y.index[0+4*last5period]- y.index[0+3*last5period]), y.index[0+4*last5period] + 2*(y.index[0+4*last5period]- y.index[0+3*last5period])],('0', str(last5period), str(2*last5period), str(3*last5period), str(4*last5period), str(5*last5period), str(6*last5period)), rotation=70)
    # plt.xticks([0, last5period, 2*last5period, 3*last5period, 4*last5period, 5*last5period, 6*last5period],('0', str(last5period), str(2*last5period), str(3*last5period), str(4*last5period), str(5*last5period), str(6*last5period)), rotation=70)
    plt.savefig(parent_folder + r'/images/' + eachMode.replace(":", "_") + targetName + '_超声刀_Sample' + b.sheets()[sheetId].name + '_下一层预测.jpg')
    plt.show()

    results_forecast = results.forecast(last5period)
    results_forecast.to_excel(parent_folder + r'/Result/' + eachMode.replace(":", "_") + targetName + '_超声刀_Sample' + b.sheets()[sheetId].name + '_下一层预测.xlsx', encoding="UTF-8", na_rep="", index=True)








sheetId=0
eachMode = 'Forward:'
sheet1 = pd.read_excel(filename, sheetname=b.sheets()[sheetId].name, header=None, encoding="UTF-8", na_rep="", index=True)
sheet1.columns = ['No', 'Mode', 'X', 'Y', 'Z', "All"]
sheet1 = sheet1[sheet1['Mode'] == eachMode]

lastNo = sheet1['No'].iloc[-1]
# noList = ['No.5', 'No.6', 'No.7', 'No.8', 'No.9']
originalFullDf = sheet1
originalFullDf.index = pd.date_range('1900-01-01', periods=len(originalFullDf), freq='D')
startIndexforEachNo = []
for eachNo in np.unique(sheet1['No']).tolist():
    eachNoDf = originalFullDf[originalFullDf['No'] == eachNo]
    startIndexforEachNo = startIndexforEachNo + [eachNoDf.index[0]]

withoutLastNoDf = sheet1.iloc[[rowId for rowId in range(len(sheet1)) if sheet1['No'].iloc[rowId] != lastNo], :]
withoutLastNoDf.index = pd.date_range('1900-01-01', periods=len(withoutLastNoDf), freq='D')

lastNoStartIndex = sheet1[sheet1['No'] == lastNo].index[0]
lastNoStartIndex = str(lastNoStartIndex.year) + '-' + str(lastNoStartIndex.month).rjust(2, '0') + '-' + str(lastNoStartIndex.day).rjust(2, '0')

last5NoList = [eachstr for eachstr in np.unique(sheet1['No']) if eachstr != lastNo]
last5NoList = last5NoList[-5:]
reallast5NoList = last5NoList[-5:] + [lastNo]
last5layers = sheet1.iloc[[rowId for rowId in range(len(sheet1)) if sheet1['No'].iloc[rowId] in last5NoList], :]
reallast5layers = sheet1.iloc[[rowId for rowId in range(len(sheet1)) if sheet1['No'].iloc[rowId] in reallast5NoList], :]
last5NoLength = last5layers['No'].value_counts()
last5period = int(np.min(last5NoLength))

for targetName in ['X', 'Y', 'Z', "All"]:
    # y = last5layers[targetName]

    allDf = []
    for eachNo in last5NoList:
        eachDf = last5layers[last5layers['No'] == eachNo]
        dropPointNum = len(eachDf) - last5period
        if len(eachDf) > last5period:
            np.random.seed(1234)
            eachDf = eachDf.iloc[[rowId for rowId in range(len(eachDf)) if rowId not in np.random.randint(5, len(eachDf)-5, [dropPointNum])], :]
            # eachDf = eachDf.iloc[:last5period, :]
        if len(allDf) == 0:
            allDf = eachDf
        else:
            allDf = pd.concat([allDf, eachDf], axis=0)

    allDf.index = pd.date_range('1900-01-01', periods=len(allDf), freq='D')

    y = allDf[targetName]
    mod = sm.tsa.statespace.SARIMAX(y,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 1, 0, last5period),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results = mod.fit()
    results_forecast = results.forecast(last5period)
    results_forecast.index = pd.date_range(lastNoStartIndex, periods=len(results_forecast), freq='D')
    plt.figure(figsize=(16, 8))
    if targetName == 'All'
        plt.title('超声刀'+'合力', fontproperties=zhfont1)
    else:
        plt.title('超声刀'+targetName, fontproperties=zhfont1)

    fullSeries = pd.DataFrame(sheet1[targetName].values.tolist() + results_forecast.values.tolist())

    plt.plot(originalFullDf[targetName], label='History')
    plt.plot(results_forecast, label='SARIMA')
    plt.legend(loc='best')
    plt.xticks(startIndexforEachNo, np.unique(sheet1['No']).tolist(), rotation=70)
    # plt.xticks([y.index[0], y.index[0+last5period], y.index[0+2*last5period], y.index[0+3*last5period], y.index[0+4*last5period], y.index[0+4*last5period] + (y.index[0+4*last5period]- y.index[0+3*last5period]), y.index[0+4*last5period] + 2*(y.index[0+4*last5period]- y.index[0+3*last5period])],('0', str(last5period), str(2*last5period), str(3*last5period), str(4*last5period), str(5*last5period), str(6*last5period)), rotation=70)
    # plt.xticks([0, last5period, 2*last5period, 3*last5period, 4*last5period, 5*last5period, 6*last5period],('0', str(last5period), str(2*last5period), str(3*last5period), str(4*last5period), str(5*last5period), str(6*last5period)), rotation=70)
    plt.savefig(parent_folder + r'/images/' + eachMode.replace(":", "_") + targetName + '_超声刀_Sample' + b.sheets()[sheetId].name + '_下一层预测.jpg')
    plt.show()

    results_forecast.to_excel(parent_folder + r'/Result/' + eachMode.replace(":", "_") + targetName + '_超声刀_Sample' + b.sheets()[sheetId].name + '_下一层预测.xlsx', encoding="UTF-8", na_rep="", index=True)

