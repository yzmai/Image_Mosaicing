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

yearmonthlyData = pd.read_excel(r'D:\Ynby\Doc\Demo/住院数据_入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)
yearmonthlyData.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in yearmonthlyData['入院年月'].values]
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

# Define the p, d and q parameters to take any value between 0 and 2
p = d = q = range(0, 2)

# Generate all different combinations of p, q and q triplets
pdq = list(itertools.product(p, d, q))

# Generate all different combinations of seasonal p, q and q triplets
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in pdq]

yearmonthlyData.rename(columns={'患者编号':'住院人数'}, inplace=True)
y = yearmonthlyData['住院人数']
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

AICDf.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院人数_ARIMA参数_AIC.xlsx', encoding="UTF-8", na_rep="", index=True)

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

mod = sm.tsa.statespace.SARIMAX(y,
                                order=(1, 1, 1),
                                seasonal_order=(1, 1, 0, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()
plt.figure(figsize=(16, 8))
plt.title('住院人数', fontproperties=zhfont1)
plt.plot(y, label='History')
plt.plot(results.forecast(12), label='SARIMA')
plt.legend(loc='best')
plt.show()
results_forecast = results.forecast(12)
results_forecast.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院人数_未来一年预测.xlsx', encoding="UTF-8", na_rep="", index=True)


y = yearmonthlyData['死亡率']
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

AICDf.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_ARIMA参数__AIC.xlsx', encoding="UTF-8", na_rep="", index=True)

mod = sm.tsa.statespace.SARIMAX(y,
                                order=(1, 0, 1),
                                seasonal_order=(0, 0, 0, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()
plt.figure(figsize=(16, 8))
plt.title('死亡率', fontproperties=zhfont1)
plt.plot(y, label='History')
plt.plot(results.forecast(12), label='SARIMA')
plt.legend(loc='best')
plt.show()

results_forecast = results.forecast(12)
results_forecast.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_未来一年预测.xlsx', encoding="UTF-8", na_rep="", index=True)

