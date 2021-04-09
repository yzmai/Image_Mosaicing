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
zhfontsmall = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=12)
zhfontmiddle = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=25)
zhfontlabel = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=18)


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

parent_folder = r'D:\Ynby\Doc\Demo\王储final'
outfolder = r'D:\Ynby\Doc\Demo\按入院时间维度_出入院时间'

deptyearmonthlyData = pd.read_excel(outfolder+r'/住院数据_科室入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)
deptyearmonthlyData.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in deptyearmonthlyData['入院年月'].values]
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

deptyearmonthlyData.rename(columns={'患者编号':'住院人数'}, inplace=True)

uniqueDepts = np.unique(deptyearmonthlyData['入院（就诊）科室名称'].values)

TestdeptyearmonthlyData = deptyearmonthlyData[deptyearmonthlyData['入院（就诊）科室名称'] == '肝胆外科病房']['住院人数']

y = TestdeptyearmonthlyData

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

optimal_param = AICDf['param'].iloc[0].replace(' ','').replace('(','').replace(')','').split(',')
optimal_param = tuple([int(eachstr) for eachstr in optimal_param])
optimal_param_seasonal = AICDf['param_seasonal'].iloc[0].replace(' ','').replace('(','').replace(')','').split(',')
optimal_param_seasonal = tuple([int(eachstr) for eachstr in optimal_param_seasonal])

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

deptTotalMergedSheet = deptyearmonthlyData.groupby(('入院（就诊）科室名称')).agg({'住院人数':'sum'})
deptTotalMergedSheet.sort_values(by='住院人数', ascending=False, inplace=True)

uniqueDepts = deptTotalMergedSheet.index.values
allDeptForecast = []
for eachDept in uniqueDepts.tolist():
    print("Enter eachDept : "+ eachDept)
    y = deptyearmonthlyData[deptyearmonthlyData['入院（就诊）科室名称'] == eachDept]['住院人数']
    # y = deptyearmonthlyData['住院人数']
    y.sort_index(ascending=True, inplace=True)
    if len(y) != 60:
        continue

    # if np.min(y) < 30:
    #     continue

    print("eachDept : "+ eachDept)

    mod = sm.tsa.statespace.SARIMAX(y,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 1, 0, 12),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results = mod.fit()
    results_forecast = results.forecast(12)
    plt.figure(figsize=(16, 8))
    plt.title(eachDept+'住院人数', fontproperties=zhfont1)
    plt.plot(y, label='History')
    plt.plot(results_forecast, label='SARIMA')
    plt.legend(loc='best')
    plt.savefig(outfolder + r'/住院数据_住院人数_未来一年预测_' + eachDept + '.jpg')
    plt.show()
    results_forecast.to_excel(outfolder + r'/住院数据_住院人数_未来一年预测_' + eachDept + '.xlsx', encoding="UTF-8", na_rep="", index=True)

    results_forecastDf = pd.DataFrame(results_forecast)
    results_forecastDf['入院（就诊）科室名称'] = eachDept
    results_forecastDf.rename(columns={0: "入院人数"}, inplace=True)
    if len(allDeptForecast) == 0:
        allDeptForecast = results_forecastDf
    else:
        allDeptForecast = pd.concat([allDeptForecast, results_forecastDf], axis=0)

allDeptForecast['入院年月'] = [str(allDeptForecast.index[id].year) + str(allDeptForecast.index[id].month).zfill(2) for id in range(len(allDeptForecast))]
allDeptForecast['入院年月'] = allDeptForecast['入院年月'].astype(np.int64)
allDeptForecast.to_excel(outfolder + r'/住院数据_住院人数_按具体科室_未来一年预测.xlsx', encoding="UTF-8", na_rep="", index=True)


inoutdeptDf = pd.read_excel(r'D:\Ynby\Doc\Demo\科室分科_内外科_北大人民医院.xlsx', sheetname='Sheet1')
inoutdeptyearmonthlyData = pd.merge(deptyearmonthlyData, inoutdeptDf, on='入院（就诊）科室名称')
inoutdeptyearmonthlyData = inoutdeptyearmonthlyData.groupby(('科室', '入院年月')).agg({'住院人数':'sum','是否死亡':'sum', '住院天数':'mean'})
inoutdeptyearmonthlyData = inoutdeptyearmonthlyData.sort_values(by='住院人数', ascending=False)
inoutdeptyearmonthlyData.reset_index(inplace=True)
inoutdeptyearmonthlyData.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in inoutdeptyearmonthlyData['入院年月'].values]
inoutdeptyearmonthlyData.sort_index(inplace=True, ascending=True)

uniqueInoutDepts = np.unique(inoutdeptDf['科室'].values).tolist()
allInoutDeptForecast = []
for eachDept in uniqueInoutDepts:
    print("Enter eachDept : "+ eachDept)
    y = inoutdeptyearmonthlyData[inoutdeptyearmonthlyData['科室'] == eachDept]['住院人数']
    y.sort_index(ascending=True, inplace=True)
    if len(y) != 60:
        continue

    # if np.min(y) < 30:
    #     continue
    print("eachDept : "+ eachDept)

    mod = sm.tsa.statespace.SARIMAX(y,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 1, 0, 12),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results = mod.fit()
    results_forecast = results.forecast(12)
    plt.figure(figsize=(16, 8))
    plt.title(eachDept+'住院人数', fontproperties=zhfont1)
    plt.plot(y, label='History')
    plt.plot(results_forecast, label='SARIMA')
    plt.legend(loc='best')
    plt.savefig(outfolder + r'/住院数据_住院人数_未来一年预测_' + eachDept + '.jpg')
    plt.show()
    results_forecast.to_excel(outfolder + r'/住院数据_住院人数_未来一年预测_' + eachDept + '.xlsx', encoding="UTF-8", na_rep="", index=True)

    results_forecastDf = pd.DataFrame(results_forecast)
    results_forecastDf['科室'] = eachDept
    results_forecastDf.rename(columns={0: "入院人数"}, inplace=True)
    if len(allInoutDeptForecast) == 0:
        allInoutDeptForecast = results_forecastDf
    else:
        allInoutDeptForecast = pd.concat([allInoutDeptForecast, results_forecastDf], axis=0)

allInoutDeptForecast['入院年月'] = [str(allInoutDeptForecast.index[id].year) + str(allInoutDeptForecast.index[id].month).zfill(2) for id in range(len(allInoutDeptForecast))]
allInoutDeptForecast['入院年月'] = allInoutDeptForecast['入院年月'].astype(np.int64)
allInoutDeptForecast.to_excel(outfolder + r'/住院数据_住院人数_按科室分类_未来一年预测.xlsx', encoding="UTF-8", na_rep="", index=True)


mergedSheet = pd.read_excel(parent_folder + r'\2019-9至2020-8就诊基本信息.xlsx', sheetname='就诊基本信息')
mergedSheet.dropna(inplace=True, subset=['入院（就诊）时间', '出院日期'])
mergedSheet['入院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['入院（就诊）时间']]
mergedSheet['入院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['入院（就诊）时间']]
mergedSheet['出院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['出院日期']]
mergedSheet['出院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['出院日期']]
datetime_in = [datetime.datetime.strptime(eachdatetime, "%Y-%m-%d %H:%M:%S") for eachdatetime in mergedSheet['入院（就诊）时间']]
datetime_out = [datetime.datetime.strptime(eachdatetime, "%Y-%m-%d %H:%M:%S") for eachdatetime in mergedSheet['出院日期']]
mergedSheet['住院天数_出入院时间'] = [(datetime_out[rowId] - datetime_in[rowId]).days for rowId in range(len(mergedSheet))]
mergedSheet['入院年月'] = [int(str(eachstr.year) + str(eachstr.month).rjust(2, '0')) for eachstr in datetime_in]

realDeptyearmonthlyMergedSheet = mergedSheet.groupby(('入院（就诊）科室名称', '入院年月')).agg({'患者编号':'count'})
realDeptyearmonthlyMergedSheet.reset_index(inplace=True)
realinoutDeptyearmonthlyMergedSheet = pd.merge(realDeptyearmonthlyMergedSheet, inoutdeptDf, on='入院（就诊）科室名称')
realinoutDeptyearmonthlyMergedSheet.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in realinoutDeptyearmonthlyMergedSheet['入院年月'].values]
realinoutDeptyearmonthlyMergedSheet.rename(columns={'患者编号':'实际入院人数'}, inplace=True)
realDeptyearmonthlyMergedSheet.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in realDeptyearmonthlyMergedSheet['入院年月'].values]
realDeptyearmonthlyMergedSheet.rename(columns={'患者编号':'实际入院人数'}, inplace=True)

realinoutDeptyearmonthlyMergedSheet.to_excel(outfolder+r'/实际住院数据_科室入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)

realinoutDeptyearmonthlyMergedSheet = realinoutDeptyearmonthlyMergedSheet.groupby(('科室', '入院年月')).agg({'实际入院人数':'sum'})
realinoutDeptyearmonthlyMergedSheet.reset_index(inplace=True)
realinoutDeptyearmonthlyMergedSheet.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in realinoutDeptyearmonthlyMergedSheet['入院年月'].values]
realinoutDeptyearmonthlyMergedSheet.to_excel(outfolder+r'/实际住院数据_科室分类_入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)

realandforecastDeptData = pd.merge(realDeptyearmonthlyMergedSheet, allDeptForecast, on=['入院（就诊）科室名称','入院年月'])
realandforecastDeptData['实际预测比'] = realandforecastDeptData['实际入院人数'] /  realandforecastDeptData['入院人数']
realandforecastDeptData.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in realandforecastDeptData['入院年月'].values]
realandforecastDeptData.to_excel(outfolder+r'/实际住院数据_科室入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)

realandforecastinoutDeptData = pd.merge(realinoutDeptyearmonthlyMergedSheet, allInoutDeptForecast, on=['科室','入院年月'])
realandforecastinoutDeptData['实际预测比'] = realandforecastinoutDeptData['实际入院人数'] /  realandforecastinoutDeptData['入院人数']
realandforecastinoutDeptData.index=[datetime.datetime.strptime(str(eachstr)[0:4]+"-"+str(eachstr)[4:6]+'-01', '%Y-%m-%d') for eachstr in realandforecastinoutDeptData['入院年月'].values]
realandforecastinoutDeptData.to_excel(outfolder+r'/实际住院数据_科室分类_入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)

Covid19_realandforecastDeptData = realandforecastDeptData[realandforecastDeptData.index >= '2020-02-01']
Covid19_realandforecastDeptData = Covid19_realandforecastDeptData.groupby(('入院（就诊）科室名称')).agg({'入院人数':'sum', '实际入院人数':'sum'})
Covid19_realandforecastDeptData['实际预测比'] = Covid19_realandforecastDeptData['实际入院人数'] /  Covid19_realandforecastDeptData['入院人数']
Covid19_realandforecastDeptData.sort_values(by='实际预测比', ascending=True, inplace=True)
Covid19_realandforecastDeptData.to_excel(outfolder+r'/实际住院数据_2020年2月新冠爆发后_科室入院人数统计.xlsx', encoding="UTF-8", na_rep="", index=True)


Covid19_realandforecastinoutDeptData = realandforecastinoutDeptData[realandforecastinoutDeptData.index >= '2020-02-01']
Covid19_realandforecastinoutDeptData = Covid19_realandforecastinoutDeptData.groupby(('科室')).agg({'入院人数':'sum', '实际入院人数':'sum'})
Covid19_realandforecastinoutDeptData['实际预测比'] = Covid19_realandforecastinoutDeptData['实际入院人数'] /  Covid19_realandforecastinoutDeptData['入院人数']
Covid19_realandforecastinoutDeptData.sort_values(by='实际预测比', ascending=True, inplace=True)
Covid19_realandforecastinoutDeptData.to_excel(outfolder+r'/实际住院数据_2020年2月新冠爆发后_科室分类_入院人数统计.xlsx', encoding="UTF-8", na_rep="", index=True)

Covid19_realandforecastDeptData.reset_index(inplace=True)
Covid19_realandforecastinoutDeptData.reset_index(inplace=True)

Covid19_realandforecastDeptData = Covid19_realandforecastDeptData[Covid19_realandforecastDeptData['入院人数'] > 200]
fig, ax = plt.subplots()
ax.set_xticks(list(range(len(Covid19_realandforecastDeptData))), minor=False)
ax.yaxis.grid(True, which='major', linewidth=2)
plt.bar(list(range(len(Covid19_realandforecastDeptData))), Covid19_realandforecastDeptData['实际预测比'])
plt.margins(0.01)
plt.ylabel("实际与预测入院人数比", fontproperties=zhfontlabel)
plt.xticks(list(range(len(Covid19_realandforecastDeptData))),tuple([eachstr.replace('病房','') for eachstr in Covid19_realandforecastDeptData['入院（就诊）科室名称'].values.tolist()]), fontproperties=zhfontsmall, rotation=270)
plt.savefig(outfolder + r'/住院数据_住院人数_2020年2月新冠爆发后_实际与预测比率_科室排序.jpg')
plt.show()


Covid19_realandforecastinoutDeptData = Covid19_realandforecastinoutDeptData[Covid19_realandforecastinoutDeptData['入院人数'] > 200]
fig, ax = plt.subplots()
ax.set_xticks(list(range(len(Covid19_realandforecastinoutDeptData))), minor=False)
ax.yaxis.grid(True, which='major', linewidth=2)
plt.bar(list(range(len(Covid19_realandforecastinoutDeptData))), Covid19_realandforecastinoutDeptData['实际预测比'])
plt.margins(0.01)
plt.ylabel("实际与预测入院人数比", fontproperties=zhfontmiddle)
plt.xticks(list(range(len(Covid19_realandforecastinoutDeptData))),tuple([eachstr.replace('病房','') for eachstr in Covid19_realandforecastinoutDeptData['科室'].values.tolist()]), fontproperties=zhfontmiddle, rotation=270)
plt.savefig(outfolder + r'/住院数据_住院人数_2020年2月新冠爆发后_实际与预测比率_科室分类排序.jpg')
plt.show()



