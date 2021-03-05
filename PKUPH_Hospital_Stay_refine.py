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
import PKUPH_trend_seasonal_residual as PKUPH_tsr

zhfont1 = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=20)

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# https://chenzhen.blog.csdn.net/article/details/103378351?utm_term=z%E6%A3%80%E9%AA%8C&utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~sobaiduweb~default-1-103378351&spm=3001.4430

parent_folder = r'D:\Ynby\Doc\Demo\王储final'
hospital_in_list = os.listdir(parent_folder)
# calendarData = calendar.get_all_calendar()

calendarData = pd.read_csv(r'D:\Ynby\Doc\Demo/calendar_new.csv', encoding='UTF-8')
calendarData.drop('Unnamed: 0', axis=1, inplace=True)
calendarData.drop('Unnamed: 0.1', axis=1, inplace=True)

holidayDict = {'工作日非周末' : 0, '工作日周末' : 1, '休息日周末' : 2, '法定假日及连休周末' : 3}
# newholidayDict = {'工作日非周末' : 0, '工作日周末' : 1, '一般周末' : 2, '两天以内法定假' : 3, '三天以上连休' : 4}
# holidayDict = {'weekday' : 0, 'workingweekend' : 1, 'normalweekend' : 2, 'holiday' : 3}
calendarData['工作日周末节假'] = np.nan
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 1)[0]), set(np.where(calendarData['holiday'] == True)[0])))] = 3
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 0)[0]), set(np.where(calendarData['holiday'] == True)[0])))] = 2
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 2)[0]), set(np.where(calendarData['holiday'] == False)[0])))] = 1
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 0)[0]), set(np.where(calendarData['holiday'] == False)[0])))] = 0
calendarData['工作日周末节假'] = calendarData['工作日周末节假'].astype(np.int16)
# calendarData['date'] = [datetime.datetime.strftime(eachstr, "%Y-%m-%d") for eachstr in calendarData['date']]
colId = np.where(calendarData.columns == '工作日周末节假')[0][0]
for dateId in range(len(calendarData)):
    if dateId+2 >= len(calendarData):
        continue
    if (calendarData['工作日周末节假'].iloc[dateId] == 2) & (calendarData['工作日周末节假'].iloc[dateId+1] == 2) & (calendarData['工作日周末节假'].iloc[dateId+2] == 3):
        calendarData.iloc[dateId, colId] = 3
        calendarData.iloc[dateId+1, colId] = 3
    if (calendarData['工作日周末节假'].iloc[dateId] == 3) & (calendarData['工作日周末节假'].iloc[dateId+1] == 2) & (calendarData['工作日周末节假'].iloc[dateId+2] == 2):
        calendarData.iloc[dateId+1, colId] = 3
        calendarData.iloc[dateId+2, colId] = 3

calendarData.to_excel(r'D:\Ynby\Doc\Demo/calendarData.xlsx', encoding="UTF-8", na_rep="", index=True)

calendarData_in = calendarData.rename(columns = {'date' : '入院Date', '工作日周末节假' : '入院工作日周末节假'})
calendarData_out = calendarData.rename(columns = {'date' : '出院Date', '工作日周末节假' : '出院工作日周末节假'})
calendarData_in = calendarData_in.iloc[:, [eachcolId for eachcolId in range(len(calendarData_in.columns)) if calendarData_in.columns.values[eachcolId] in ['入院Date', '入院工作日周末节假']]]
calendarData_out = calendarData_out.iloc[:, [eachcolId for eachcolId in range(len(calendarData_out.columns)) if calendarData_out.columns.values[eachcolId] in ['出院Date', '出院工作日周末节假']]]

allMergedSheet = []
for filename in hospital_in_list:
    if filename.find('201') == 0:
        b = xlrd.open_workbook(os.path.join(parent_folder, filename))
        sheet_gender = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[0].name)
        sheet_hosp = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[1].name)
        sheet_death = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[2].name)
        if '就诊类别名称' in sheet_hosp.columns.values:
            sheet_hosp.drop('就诊类别名称', axis=1, inplace=True)
        if 'EMR.就诊.就诊基本信息.就诊类别名称' in sheet_hosp.columns.values:
            sheet_hosp.drop('EMR.就诊.就诊基本信息.就诊类别名称', axis=1, inplace=True)

        sheet_hosp.rename(columns={'EMR.就诊.就诊基本信息.住院天数' : '住院天数', 'EMR.就诊.就诊基本信息.入院（就诊）科室名称' : '入院（就诊）科室名称',  \
                                   'EMR.就诊.就诊基本信息.入院（就诊）时间' : '入院（就诊）时间', 'EMR.就诊.就诊基本信息.出院科室名称' : '出院科室名称',  \
                                   'EMR.就诊.就诊基本信息.出院日期' : '出院日期', 'EMR.就诊.就诊基本信息.就诊年龄（岁）' : '就诊年龄（岁）'}, inplace=True)
        sheet_death['是否死亡'] = 1
        sheet_death = sheet_death.iloc[:, [eachcolId for eachcolId in range(len(sheet_death.columns)) if sheet_death.columns.values[eachcolId] in ['患者编号', '入院（就诊）时间', '是否死亡']]]

        mergedSheet = pd.merge(sheet_gender, sheet_hosp, on = '患者编号')
        mergedSheet = pd.merge(mergedSheet, sheet_death, on = ['患者编号', '入院（就诊）时间'], how='left')
        mergedSheet['是否死亡'][np.isnan(mergedSheet['是否死亡'])] = 0

        mergedSheet['入院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['入院（就诊）时间']]
        mergedSheet['入院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['入院（就诊）时间']]
        mergedSheet['出院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['出院日期']]
        mergedSheet['出院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['出院日期']]
        datetime_in = [datetime.datetime.strptime(eachdatetime, "%Y-%m-%d %H:%M:%S") for eachdatetime in mergedSheet['入院（就诊）时间']]
        datetime_out = [datetime.datetime.strptime(eachdatetime, "%Y-%m-%d %H:%M:%S") for eachdatetime in mergedSheet['出院日期']]
        mergedSheet['入院年份'] = [eachstr.year for eachstr in datetime_in]
        mergedSheet['入院月份'] = [eachstr.month for eachstr in datetime_in]
        mergedSheet['入院年月'] = [int(str(eachstr.year)+str(eachstr.month).rjust(2, '0')) for eachstr in datetime_in]
        mergedSheet['入院日期'] = [eachstr.day for eachstr in datetime_in]
        mergedSheet['入院周几'] = [eachstr.weekday() for eachstr in datetime_in]
        mergedSheet['入院小时'] = [eachstr.hour for eachstr in datetime_in]
        mergedSheet['出院年份'] = [eachstr.year for eachstr in datetime_out]
        mergedSheet['出院月份'] = [eachstr.month for eachstr in datetime_out]
        mergedSheet['出院年月'] = [int(str(eachstr.year)+str(eachstr.month).rjust(2, '0')) for eachstr in datetime_out]
        mergedSheet['出院日期'] = [eachstr.day for eachstr in datetime_out]
        mergedSheet['出院周几'] = [eachstr.weekday() for eachstr in datetime_out]
        mergedSheet['出院小时'] = [eachstr.hour for eachstr in datetime_out]

        mergedSheet = pd.merge(mergedSheet, calendarData_in, on = '入院Date', how='left')
        mergedSheet = pd.merge(mergedSheet, calendarData_out, on = '出院Date', how='left')

        if len(allMergedSheet) == 0:
            allMergedSheet = mergedSheet
        else:
            allMergedSheet = pd.concat([allMergedSheet, mergedSheet], axis=0)

# allMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/allMergedSheet.xlsx', encoding="UTF-8", na_rep="", index=True)

yearmonthlyMergedSheet = allMergedSheet.groupby('入院年月').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearmonthlyMergedSheet['死亡率'] = yearmonthlyMergedSheet['是否死亡'] / yearmonthlyMergedSheet['患者编号']
yearmonthlyMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_入院年月统计.xlsx', encoding="UTF-8", na_rep="", index=True)


fig, ax = plt.subplots()
ax.set_xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54], minor=False)
ax.xaxis.grid(True, which='major', linewidth=2)
plt.plot(list(range(len(yearmonthlyMergedSheet.index))), yearmonthlyMergedSheet['住院天数'].values,'-*')
plt.title(u'2014-2019每月平均住院天数', fontproperties=zhfont1)
plt.xlabel('年月', fontproperties=zhfont1)
plt.ylabel('住院天数', fontproperties=zhfont1)
plt.legend(prop=zhfont1)
plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
plt.savefig(r'D:\Ynby\Doc\Demo/2014-2019每月平均住院天数.jpg')
plt.show()

#设置横纵坐标的名称以及对应字体格式
font2 = {'family' : 'Times New Roman', 'weight' : 'normal', 'size' : 30}
fig, ax = plt.subplots()
ax.set_xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54], minor=False)
ax.xaxis.grid(True, which='major', linewidth=2)
plt.plot(list(range(len(yearmonthlyMergedSheet.index))), yearmonthlyMergedSheet['死亡率'].values,'-*')
plt.title(u'2014-2019每月死亡率', fontproperties=zhfont1)
plt.xlabel('年月', fontproperties=zhfont1)
plt.ylabel('死亡率', fontproperties=zhfont1)
plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
plt.savefig(r'D:\Ynby\Doc\Demo/2014-2019每月死亡率.jpg')
plt.show()


yearlyMergedSheet = allMergedSheet.groupby('入院年份').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearlyMergedSheet['死亡率'] = yearlyMergedSheet['是否死亡'] / yearlyMergedSheet['患者编号']
yearlyMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_入院年份统计.xlsx', encoding="UTF-8", na_rep="", index=True)

yearlyindeptMergedSheet = allMergedSheet.groupby(by=('入院年份', '入院（就诊）科室名称')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearlyindeptMergedSheet['死亡率'] = yearlyindeptMergedSheet['是否死亡'] / yearlyindeptMergedSheet['患者编号']
yearlyoutdeptMergedSheet = allMergedSheet.groupby(by=('入院年份', '出院科室名称')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearlyoutdeptMergedSheet['死亡率'] = yearlyoutdeptMergedSheet['是否死亡'] / yearlyoutdeptMergedSheet['患者编号']

monthlyindeptMergedSheet = allMergedSheet.groupby(by=('入院月份', '入院（就诊）科室名称')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
monthlyindeptMergedSheet['死亡率'] = monthlyindeptMergedSheet['是否死亡'] / monthlyindeptMergedSheet['患者编号']
monthlyoutdeptMergedSheet = allMergedSheet.groupby(by=('入院月份', '出院科室名称')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
monthlyoutdeptMergedSheet['死亡率'] = monthlyoutdeptMergedSheet['是否死亡'] / monthlyoutdeptMergedSheet['患者编号']
monthlyoutdeptMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_入院月度科室统计.xlsx', encoding="UTF-8", na_rep="", index=True)

monthlyMergedSheet = allMergedSheet.groupby('入院月份').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
monthlyMergedSheet['死亡率'] = monthlyMergedSheet['是否死亡'] / monthlyMergedSheet['患者编号']
monthlyMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_入院月度统计.xlsx', encoding="UTF-8", na_rep="", index=True)



fig, ax = plt.subplots()
plt.plot(list(range(1, 13)), monthlyMergedSheet['住院天数'].values, '-*')
# plt.plot(list(range(len(yearmonthlyMergedSheet.index))), yearmonthlyMergedSheet['住院天数'].values,'-*')
plt.title(u'按月份平均住院天数', fontproperties=zhfont1)
plt.xlabel('月份', fontproperties=zhfont1)
plt.ylabel('住院天数', fontproperties=zhfont1)
plt.legend(prop=zhfont1)
# plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
plt.savefig(r'D:\Ynby\Doc\Demo/按月份平均住院天数.jpg')
plt.show()

fig, ax = plt.subplots()
plt.plot(list(range(1, 13)), monthlyMergedSheet['死亡率'].values, '-*')
# plt.plot(list(range(len(yearmonthlyMergedSheet.index))), yearmonthlyMergedSheet['住院天数'].values,'-*')
plt.title(u'按月份死亡率', fontproperties=zhfont1)
plt.xlabel('月份', fontproperties=zhfont1)
plt.ylabel('死亡率', fontproperties=zhfont1)
plt.legend(prop=zhfont1)
# plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
plt.savefig(r'D:\Ynby\Doc\Demo/按月份死亡率.jpg')
plt.show()

#除去节假日
noholidayallMergedSheet = allMergedSheet[allMergedSheet['入院工作日周末节假'] != 3]
noholidaymonthlyMergedSheet = noholidayallMergedSheet.groupby('入院月份').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
noholidaymonthlyMergedSheet['死亡率'] = noholidaymonthlyMergedSheet['是否死亡'] / noholidaymonthlyMergedSheet['患者编号']
noholidaymonthlyMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_无节假日_入院月度统计.xlsx', encoding="UTF-8", na_rep="", index=True)

fig, ax = plt.subplots()
plt.plot(list(range(1, 13)), noholidaymonthlyMergedSheet['住院天数'].values, '-*')
# plt.plot(list(range(len(yearmonthlyMergedSheet.index))), yearmonthlyMergedSheet['住院天数'].values,'-*')
plt.title(u'按月份平均住院天数(排除节假日)', fontproperties=zhfont1)
plt.xlabel('月份', fontproperties=zhfont1)
plt.ylabel('住院天数', fontproperties=zhfont1)
plt.legend(prop=zhfont1)
# plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
plt.savefig(r'D:\Ynby\Doc\Demo/除节假日按月份平均住院天数.jpg')
plt.show()

fig, ax = plt.subplots()
plt.plot(list(range(1, 13)), noholidaymonthlyMergedSheet['死亡率'].values, '-*')
# plt.plot(list(range(len(yearmonthlyMergedSheet.index))), yearmonthlyMergedSheet['住院天数'].values,'-*')
plt.title(u'按月份死亡率(排除节假日)', fontproperties=zhfont1)
plt.xlabel('月份', fontproperties=zhfont1)
plt.ylabel('死亡率', fontproperties=zhfont1)
plt.legend(prop=zhfont1)
# plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
plt.savefig(r'D:\Ynby\Doc\Demo/除节假日按月份死亡率.jpg')
plt.show()



weeklyMergedSheet = allMergedSheet.groupby('入院周几').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
weeklyMergedSheet['死亡率'] = weeklyMergedSheet['是否死亡'] / weeklyMergedSheet['患者编号']
weeklyMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_入院周几统计.xlsx', encoding="UTF-8", na_rep="", index=True)

hourlyMergedSheet = allMergedSheet.groupby('入院小时').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
hourlyMergedSheet['死亡率'] = hourlyMergedSheet['是否死亡'] / hourlyMergedSheet['患者编号']
weekdayendholidayMergedSheet = allMergedSheet.groupby('入院工作日周末节假').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
weekdayendholidayMergedSheet['死亡率'] = weekdayendholidayMergedSheet['是否死亡'] / weekdayendholidayMergedSheet['患者编号']
weekdayendholidayMergedSheet.index = list(holidayDict.keys())
weekdayendholidayMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_入院工作日周末节假统计.xlsx', encoding="UTF-8", na_rep="", index=True)

genderMergedSheet = allMergedSheet.groupby('性别').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
genderMergedSheet['死亡率'] = genderMergedSheet['是否死亡'] / genderMergedSheet['患者编号']
genderMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_性别统计.xlsx', encoding="UTF-8", na_rep="", index=True)

ageMergedSheet = allMergedSheet.groupby('就诊年龄（岁）').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
ageMergedSheet['死亡率'] = ageMergedSheet['是否死亡'] / ageMergedSheet['患者编号']
ageMergedSheet = ageMergedSheet.sort_values(by='死亡率', ascending=False)

deptMergedSheet = allMergedSheet.groupby('入院（就诊）科室名称').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
deptMergedSheet['死亡率'] = deptMergedSheet['是否死亡'] / deptMergedSheet['患者编号']
deptMergedSheet = deptMergedSheet.sort_values(by='死亡率', ascending=False)
deptMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_科室统计.xlsx', encoding="UTF-8", na_rep="", index=True)



#年份变化
years = np.unique(allMergedSheet['入院年份'].values)
staydays_year_ztest_mean = np.zeros((len(years), len(years)))
staydays_year_ztest_p = np.zeros((len(years), len(years)))
death_year_ztest_mean = np.zeros((len(years), len(years)))
death_year_ztest_p = np.zeros((len(years), len(years)))

for rowyearId in range(len(years)):
    for colyearId in range(len(years)):
        list1= allMergedSheet[allMergedSheet['入院年份'] == years[rowyearId]]['住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院年份'] == years[colyearId]]['住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_year_ztest_mean[rowyearId, colyearId] = ztest[0]
        staydays_year_ztest_p[rowyearId, colyearId] = ztest[1]

        list1= allMergedSheet[allMergedSheet['入院年份'] == years[rowyearId]]['是否死亡'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院年份'] == years[colyearId]]['是否死亡'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        death_year_ztest_mean[rowyearId, colyearId] = ztest[0]
        death_year_ztest_p[rowyearId, colyearId] = ztest[1]


staydays_year_ztest_p = pd.DataFrame(staydays_year_ztest_p)
staydays_year_ztest_p.columns=years
staydays_year_ztest_p.index=years
staydays_year_ztest_p = pd.DataFrame(np.round(staydays_year_ztest_p, 5))
death_year_ztest_p = pd.DataFrame(death_year_ztest_p)
death_year_ztest_p.columns=years
death_year_ztest_p.index=years
death_year_ztest_p = pd.DataFrame(np.round(death_year_ztest_p, 5))

staydays_year_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_按年份z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
death_year_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_按年份z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)


#月份变化
months = np.unique(allMergedSheet['入院月份'].values)
staydays_month_ztest_mean = np.zeros((len(months), len(months)))
staydays_month_ztest_p = np.zeros((len(months), len(months)))
death_month_ztest_mean = np.zeros((len(months), len(months)))
death_month_ztest_p = np.zeros((len(months), len(months)))

for rowmonthId in range(len(months)):
    for colmonthId in range(len(months)):
        list1= allMergedSheet[allMergedSheet['入院月份'] == months[rowmonthId]]['住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院月份'] == months[colmonthId]]['住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_month_ztest_mean[rowmonthId, colmonthId] = ztest[0]
        staydays_month_ztest_p[rowmonthId, colmonthId] = ztest[1]

        list1= allMergedSheet[allMergedSheet['入院月份'] == months[rowmonthId]]['是否死亡'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院月份'] == months[colmonthId]]['是否死亡'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        death_month_ztest_mean[rowmonthId, colmonthId] = ztest[0]
        death_month_ztest_p[rowmonthId, colmonthId] = ztest[1]


staydays_month_ztest_p = pd.DataFrame(staydays_month_ztest_p)
staydays_month_ztest_p.columns=months
staydays_month_ztest_p.index=months
staydays_month_ztest_p = pd.DataFrame(np.round(staydays_month_ztest_p, 5))
death_month_ztest_p = pd.DataFrame(death_month_ztest_p)
death_month_ztest_p.columns=months
death_month_ztest_p.index=months
death_month_ztest_p = pd.DataFrame(np.round(death_month_ztest_p, 5))

staydays_month_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_按自然月z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
death_month_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_按自然月z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)



#去除趋势月份变化
trend_stayday, seasonal, residual = PKUPH_tsr.get_trend_seasonal_residual('住院天数')
trend_death, seasonal, residual = PKUPH_tsr.get_trend_seasonal_residual('死亡率')
trend_patientnum, seasonal, residual = PKUPH_tsr.get_trend_seasonal_residual('患者编号')
allMergedSheet['入院Date'] = allMergedSheet['入院Date'].astype('str')
trend_stayday = trend_stayday.reset_index()
trend_stayday.rename(columns={'入院年月': '入院年月月初', '住院天数': '住院天数趋势'}, inplace=True)
trend_death = trend_death.reset_index()
trend_death.rename(columns={'入院年月': '入院年月月初', '住院天数': '死亡率趋势'}, inplace=True)
trend_patientnum = trend_patientnum.reset_index()
trend_patientnum.rename(columns={'入院年月': '入院年月月初', '住院天数': '死亡率趋势'}, inplace=True)

allMergedSheet['入院年月月初'] = [(str(eachint)[0:4] + '-' + str(eachint)[4:6] + '-01') for eachint in allMergedSheet['入院年月'].values]

trend_stayday['入院年月月初'] = [datetime.datetime.strftime(eachstr, "%Y-%m-%d") for eachstr in trend_stayday['入院年月月初']]
trend_death['入院年月月初'] = [datetime.datetime.strftime(eachstr, "%Y-%m-%d") for eachstr in trend_death['入院年月月初']]
notrendallMergedSheet = pd.merge(allMergedSheet, trend_stayday, on ='入院年月月初')
notrendallMergedSheet['去除趋势住院天数'] = notrendallMergedSheet['住院天数'] - notrendallMergedSheet['住院天数趋势']
notrendallMergedSheet = notrendallMergedSheet[np.isnan(notrendallMergedSheet['住院天数']) == False]
notrendallMergedSheet['去除趋势死亡率'] = notrendallMergedSheet['死亡率'] - notrendallMergedSheet['死亡率趋势']
notrendallMergedSheet = notrendallMergedSheet[np.isnan(notrendallMergedSheet['住院天数']) == False]

months = np.unique(notrendallMergedSheet['入院月份'].values)
staydays_month_ztest_mean = np.zeros((len(months), len(months)))
staydays_month_ztest_p = np.zeros((len(months), len(months)))
death_month_ztest_mean = np.zeros((len(months), len(months)))
death_month_ztest_p = np.zeros((len(months), len(months)))

for rowmonthId in range(len(months)):
    for colmonthId in range(len(months)):
        list1= notrendallMergedSheet[notrendallMergedSheet['入院月份'] == months[rowmonthId]]['去除趋势住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= notrendallMergedSheet[notrendallMergedSheet['入院月份'] == months[colmonthId]]['去除趋势住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_month_ztest_mean[rowmonthId, colmonthId] = ztest[0]
        staydays_month_ztest_p[rowmonthId, colmonthId] = ztest[1]

        # list1= notrendallMergedSheet[notrendallMergedSheet['入院月份'] == months[rowmonthId]]['是否死亡'].values
        # list1 = list1[np.isnan(list1) == False]
        # list2= notrendallMergedSheet[notrendallMergedSheet['入院月份'] == months[colmonthId]]['是否死亡'].values
        # list2 = list2[np.isnan(list2) == False]
        # ztest = sw.ztest(list1, list2)
        # death_month_ztest_mean[rowmonthId, colmonthId] = ztest[0]
        # death_month_ztest_p[rowmonthId, colmonthId] = ztest[1]


staydays_month_ztest_p = pd.DataFrame(staydays_month_ztest_p)
staydays_month_ztest_p.columns=months
staydays_month_ztest_p.index=months
staydays_month_ztest_p = pd.DataFrame(np.round(staydays_month_ztest_p, 5))
# death_month_ztest_p = pd.DataFrame(death_month_ztest_p)
# death_month_ztest_p.columns=months
# death_month_ztest_p.index=months
# death_month_ztest_p = pd.DataFrame(np.round(death_month_ztest_p, 5))

staydays_month_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_去除趋势按自然月z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
# death_month_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_去除趋势按自然月z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)




#去除节假日的月份变化
months = np.unique(noholidayallMergedSheet['入院月份'].values)
staydays_month_ztest_mean = np.zeros((len(months), len(months)))
staydays_month_ztest_p = np.zeros((len(months), len(months)))
death_month_ztest_mean = np.zeros((len(months), len(months)))
death_month_ztest_p = np.zeros((len(months), len(months)))

for rowmonthId in range(len(months)):
    for colmonthId in range(len(months)):
        list1= noholidayallMergedSheet[noholidayallMergedSheet['入院月份'] == months[rowmonthId]]['住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= noholidayallMergedSheet[noholidayallMergedSheet['入院月份'] == months[colmonthId]]['住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_month_ztest_mean[rowmonthId, colmonthId] = ztest[0]
        staydays_month_ztest_p[rowmonthId, colmonthId] = ztest[1]

        list1= noholidayallMergedSheet[noholidayallMergedSheet['入院月份'] == months[rowmonthId]]['是否死亡'].values
        list1 = list1[np.isnan(list1) == False]
        list2= noholidayallMergedSheet[noholidayallMergedSheet['入院月份'] == months[colmonthId]]['是否死亡'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        death_month_ztest_mean[rowmonthId, colmonthId] = ztest[0]
        death_month_ztest_p[rowmonthId, colmonthId] = ztest[1]


staydays_month_ztest_p = pd.DataFrame(staydays_month_ztest_p)
staydays_month_ztest_p.columns=months
staydays_month_ztest_p.index=months
staydays_month_ztest_p = pd.DataFrame(np.round(staydays_month_ztest_p, 5))
death_month_ztest_p = pd.DataFrame(death_month_ztest_p)
death_month_ztest_p.columns=months
death_month_ztest_p.index=months
death_month_ztest_p = pd.DataFrame(np.round(death_month_ztest_p, 5))

staydays_month_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_排除节假日按自然月z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
death_month_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_排除节假日按自然月z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)



#周几变化
weekdays = np.unique(allMergedSheet['入院周几'].values)
staydays_weekday_ztest_mean = np.zeros((len(weekdays), len(weekdays)))
staydays_weekday_ztest_p = np.zeros((len(weekdays), len(weekdays)))
death_weekday_ztest_mean = np.zeros((len(weekdays), len(weekdays)))
death_weekday_ztest_p = np.zeros((len(weekdays), len(weekdays)))

for rowweekdayId in range(len(weekdays)):
    for colweekdayId in range(len(weekdays)):
        list1= allMergedSheet[allMergedSheet['入院周几'] == weekdays[rowweekdayId]]['住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院周几'] == weekdays[colweekdayId]]['住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_weekday_ztest_mean[rowweekdayId, colweekdayId] = ztest[0]
        staydays_weekday_ztest_p[rowweekdayId, colweekdayId] = ztest[1]

        list1= allMergedSheet[allMergedSheet['入院周几'] == weekdays[rowweekdayId]]['是否死亡'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院周几'] == weekdays[colweekdayId]]['是否死亡'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        death_weekday_ztest_mean[rowweekdayId, colweekdayId] = ztest[0]
        death_weekday_ztest_p[rowweekdayId, colweekdayId] = ztest[1]


staydays_weekday_ztest_p = pd.DataFrame(staydays_weekday_ztest_p)
WEEKDAYs = ['周一','周二','周三','周四','周五','周六','周日']
staydays_weekday_ztest_p.columns=WEEKDAYs
staydays_weekday_ztest_p.index=WEEKDAYs
staydays_weekday_ztest_p = pd.DataFrame(np.round(staydays_weekday_ztest_p, 5))
death_weekday_ztest_p = pd.DataFrame(death_weekday_ztest_p)
death_weekday_ztest_p.columns=WEEKDAYs
death_weekday_ztest_p.index=WEEKDAYs
death_weekday_ztest_p = pd.DataFrame(np.round(death_weekday_ztest_p, 5))

staydays_weekday_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_按周几z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
death_weekday_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_按周几z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)


#入院工作日周末节假
weekdayendholidays = np.unique(allMergedSheet['入院工作日周末节假'].values)
staydays_weekdayendholiday_ztest_mean = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))
staydays_weekdayendholiday_ztest_p = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))
death_weekdayendholiday_ztest_mean = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))
death_weekdayendholiday_ztest_p = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))

for rowweekdayendholidayId in range(len(weekdayendholidays)):
    for colweekdayendholidayId in range(len(weekdayendholidays)):
        list1= allMergedSheet[allMergedSheet['入院工作日周末节假'] == weekdayendholidays[rowweekdayendholidayId]]['住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院工作日周末节假'] == weekdayendholidays[colweekdayendholidayId]]['住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_weekdayendholiday_ztest_mean[rowweekdayendholidayId, colweekdayendholidayId] = ztest[0]
        staydays_weekdayendholiday_ztest_p[rowweekdayendholidayId, colweekdayendholidayId] = ztest[1]

        list1= allMergedSheet[allMergedSheet['入院工作日周末节假'] == weekdayendholidays[rowweekdayendholidayId]]['是否死亡'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['入院工作日周末节假'] == weekdayendholidays[colweekdayendholidayId]]['是否死亡'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        death_weekdayendholiday_ztest_mean[rowweekdayendholidayId, colweekdayendholidayId] = ztest[0]
        death_weekdayendholiday_ztest_p[rowweekdayendholidayId, colweekdayendholidayId] = ztest[1]


WEEKDAYENDHOLIDAYS = list(holidayDict.keys())
staydays_weekdayendholiday_ztest_p = pd.DataFrame(staydays_weekdayendholiday_ztest_p)
staydays_weekdayendholiday_ztest_p.columns=WEEKDAYENDHOLIDAYS
staydays_weekdayendholiday_ztest_p.index=WEEKDAYENDHOLIDAYS
staydays_weekdayendholiday_ztest_p = pd.DataFrame(np.round(staydays_weekdayendholiday_ztest_p, 5))
death_weekdayendholiday_ztest_p = pd.DataFrame(death_weekdayendholiday_ztest_p)
death_weekdayendholiday_ztest_p.columns=WEEKDAYENDHOLIDAYS
death_weekdayendholiday_ztest_p.index=WEEKDAYENDHOLIDAYS
death_weekdayendholiday_ztest_p = pd.DataFrame(np.round(death_weekdayendholiday_ztest_p, 5))

staydays_weekdayendholiday_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_按工作日周末节假z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
death_weekdayendholiday_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_按工作日周末节假z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)


#入院工作日周末节假（排除春节）
SpringfestivalDates = ['2015-02-18', '2015-02-19', '2015-02-20', '2015-02-21', '2015-02-22', '2015-02-23', '2015-02-24', '2016-02-07', '2016-02-08', '2016-02-09', '2016-02-10', '2016-02-11', '2016-02-12', '2016-02-13', '2017-01-27', '2017-01-28', '2017-01-29', '2017-01-30', '2017-01-31', '2017-02-01', '2017-02-20',  '2018-02-15', '2018-02-16', '2018-02-17', '2018-02-18', '2018-02-19', '2018-02-20', '2018-02-21', '2019-02-04', '2019-02-05', '2019-02-06', '2019-02-07', '2019-02-08', '2019-02-09', '2019-02-10']
nospringfestivalallMergedSheet = allMergedSheet.iloc[[rowId for rowId in range(len(allMergedSheet)) if allMergedSheet['入院Date'].iloc[rowId] not in SpringfestivalDates], :]
weekdayendholidayMergedSheet = nospringfestivalallMergedSheet.groupby('入院工作日周末节假').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
weekdayendholidayMergedSheet['死亡率'] = weekdayendholidayMergedSheet['是否死亡'] / weekdayendholidayMergedSheet['患者编号']
weekdayendholidayMergedSheet.index = list(holidayDict.keys())
weekdayendholidayMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_排除春节入院工作日周末节假统计.xlsx', encoding="UTF-8", na_rep="", index=True)

weekdayendholidays = np.unique(nospringfestivalallMergedSheet['入院工作日周末节假'].values)
staydays_weekdayendholiday_ztest_mean = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))
staydays_weekdayendholiday_ztest_p = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))
death_weekdayendholiday_ztest_mean = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))
death_weekdayendholiday_ztest_p = np.zeros((len(weekdayendholidays), len(weekdayendholidays)))

for rowweekdayendholidayId in range(len(weekdayendholidays)):
    for colweekdayendholidayId in range(len(weekdayendholidays)):
        list1= nospringfestivalallMergedSheet[nospringfestivalallMergedSheet['入院工作日周末节假'] == weekdayendholidays[rowweekdayendholidayId]]['住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= nospringfestivalallMergedSheet[nospringfestivalallMergedSheet['入院工作日周末节假'] == weekdayendholidays[colweekdayendholidayId]]['住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_weekdayendholiday_ztest_mean[rowweekdayendholidayId, colweekdayendholidayId] = ztest[0]
        staydays_weekdayendholiday_ztest_p[rowweekdayendholidayId, colweekdayendholidayId] = ztest[1]

        list1= nospringfestivalallMergedSheet[nospringfestivalallMergedSheet['入院工作日周末节假'] == weekdayendholidays[rowweekdayendholidayId]]['是否死亡'].values
        list1 = list1[np.isnan(list1) == False]
        list2= nospringfestivalallMergedSheet[nospringfestivalallMergedSheet['入院工作日周末节假'] == weekdayendholidays[colweekdayendholidayId]]['是否死亡'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        death_weekdayendholiday_ztest_mean[rowweekdayendholidayId, colweekdayendholidayId] = ztest[0]
        death_weekdayendholiday_ztest_p[rowweekdayendholidayId, colweekdayendholidayId] = ztest[1]


WEEKDAYENDHOLIDAYS = list(holidayDict.keys())
staydays_weekdayendholiday_ztest_p = pd.DataFrame(staydays_weekdayendholiday_ztest_p)
staydays_weekdayendholiday_ztest_p.columns=WEEKDAYENDHOLIDAYS
staydays_weekdayendholiday_ztest_p.index=WEEKDAYENDHOLIDAYS
staydays_weekdayendholiday_ztest_p = pd.DataFrame(np.round(staydays_weekdayendholiday_ztest_p, 5))
death_weekdayendholiday_ztest_p = pd.DataFrame(death_weekdayendholiday_ztest_p)
death_weekdayendholiday_ztest_p.columns=WEEKDAYENDHOLIDAYS
death_weekdayendholiday_ztest_p.index=WEEKDAYENDHOLIDAYS
death_weekdayendholiday_ztest_p = pd.DataFrame(np.round(death_weekdayendholiday_ztest_p, 5))

staydays_weekdayendholiday_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_排除春节按工作日周末节假z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
death_weekdayendholiday_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_排除春节按工作日周末节假z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)


#性别对比
genders = ['女性', '男性']
staydays_gender_ztest_mean = np.zeros((len(genders), len(genders)))
staydays_gender_ztest_p = np.zeros((len(genders), len(genders)))
death_gender_ztest_mean = np.zeros((len(genders), len(genders)))
death_gender_ztest_p = np.zeros((len(genders), len(genders)))

for rowgenderId in range(len(genders)):
    for colgenderId in range(len(genders)):
        list1= allMergedSheet[allMergedSheet['性别'] == genders[rowgenderId]]['住院天数'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['性别'] == genders[colgenderId]]['住院天数'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        staydays_gender_ztest_mean[rowgenderId, colgenderId] = ztest[0]
        staydays_gender_ztest_p[rowgenderId, colgenderId] = ztest[1]

        list1= allMergedSheet[allMergedSheet['性别'] == genders[rowgenderId]]['是否死亡'].values
        list1 = list1[np.isnan(list1) == False]
        list2= allMergedSheet[allMergedSheet['性别'] == genders[colgenderId]]['是否死亡'].values
        list2 = list2[np.isnan(list2) == False]
        ztest = sw.ztest(list1, list2)
        death_gender_ztest_mean[rowgenderId, colgenderId] = ztest[0]
        death_gender_ztest_p[rowgenderId, colgenderId] = ztest[1]


staydays_gender_ztest_p = pd.DataFrame(staydays_gender_ztest_p)
staydays_gender_ztest_p.columns=genders
staydays_gender_ztest_p.index=genders
staydays_gender_ztest_p = pd.DataFrame(np.round(staydays_gender_ztest_p, 5))
death_gender_ztest_p = pd.DataFrame(death_gender_ztest_p)
death_gender_ztest_p.columns=genders
death_gender_ztest_p.index=genders
death_gender_ztest_p = pd.DataFrame(np.round(death_gender_ztest_p, 5))

staydays_gender_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_性别z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
death_gender_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_性别z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)




#科室对比
topdeptMergedSheet = deptMergedSheet[deptMergedSheet['死亡率'] > 0.005]
depts = np.unique(topdeptMergedSheet.index.values)
staydays_dept_ztest_mean = np.zeros((len(depts), len(depts)))
staydays_dept_ztest_p = np.zeros((len(depts), len(depts)))
death_dept_ztest_mean = np.zeros((len(depts), len(depts)))
death_dept_ztest_p = np.zeros((len(depts), len(depts)))

all_staydays_year_ztest_p = []
all_death_year_ztest_p= []

for deptId in range(len(depts)):
    #年份变化
    eachDeptMergedSheet = allMergedSheet[allMergedSheet['入院（就诊）科室名称'] == depts[deptId]]
    years = np.unique(eachDeptMergedSheet['入院年份'])
    if len(years) < 2019-2014+1:
        continue
    years = [2014, 2019]

    staydays_year_ztest_mean = np.zeros((len(years), len(years)))
    staydays_year_ztest_p = np.zeros((len(years), len(years)))
    death_year_ztest_mean = np.zeros((len(years), len(years)))
    death_year_ztest_p = np.zeros((len(years), len(years)))

    for rowyearId in range(len(years)):
        for colyearId in range(len(years)):
            list1= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[rowyearId]]['住院天数'].values
            list1 = list1[np.isnan(list1) == False]
            list2= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[colyearId]]['住院天数'].values
            list2 = list2[np.isnan(list2) == False]
            ztest = sw.ztest(list1, list2)
            staydays_year_ztest_mean[rowyearId, colyearId] = ztest[0]
            staydays_year_ztest_p[rowyearId, colyearId] = ztest[1]

            list1= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[rowyearId]]['是否死亡'].values
            list1 = list1[np.isnan(list1) == False]
            list2= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[colyearId]]['是否死亡'].values
            list2 = list2[np.isnan(list2) == False]
            ztest = sw.ztest(list1, list2)
            death_year_ztest_mean[rowyearId, colyearId] = ztest[0]
            death_year_ztest_p[rowyearId, colyearId] = ztest[1]


    staydays_year_ztest_p = pd.DataFrame(staydays_year_ztest_p).iloc[0:1, 1:2]
    staydays_year_ztest_p['科室'] = depts[deptId]
    if len(all_staydays_year_ztest_p) != 0:
        all_staydays_year_ztest_p = pd.concat([all_staydays_year_ztest_p, staydays_year_ztest_p], axis=0)
    else:
        all_staydays_year_ztest_p = staydays_year_ztest_p

    death_year_ztest_p = pd.DataFrame(death_year_ztest_p).iloc[0:1, 1:2]
    death_year_ztest_p = pd.DataFrame(np.round(death_year_ztest_p, 5))
    death_year_ztest_p['科室'] = depts[deptId]
    if len(all_death_year_ztest_p) != 0:
        all_death_year_ztest_p = pd.concat([all_death_year_ztest_p, death_year_ztest_p], axis=0)
    else:
        all_death_year_ztest_p = death_year_ztest_p

all_staydays_year_ztest_p.rename(columns={1: '住院天数p值'}, inplace=True)
all_staydays_year_ztest_p.sort_values(by='住院天数p值', ascending=True, inplace=True)
all_death_year_ztest_p.rename(columns={1: '死亡率p值'}, inplace=True)
all_death_year_ztest_p.sort_values(by='死亡率p值', ascending=True, inplace=True)


all_staydays_year_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_入院科室2014到2019变化z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
all_death_year_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_入院科室2014到2019变化z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)

allMergedSheet_onlytopDept = allMergedSheet.iloc[[rowId for rowId in range(len(allMergedSheet)) if allMergedSheet['入院（就诊）科室名称'].iloc[rowId] in all_death_year_ztest_p['科室'].tolist()], :]
allMergedSheet_2014_onlytopDept = allMergedSheet_onlytopDept[allMergedSheet_onlytopDept['入院年份'] == 2014]
allMergedSheet_2019_onlytopDept = allMergedSheet_onlytopDept[allMergedSheet_onlytopDept['入院年份'] == 2019]
allMergedSheet_2014and2019_onlytopDept = pd.concat([allMergedSheet_2014_onlytopDept, allMergedSheet_2019_onlytopDept], axis=0)
deptMergedSheet_2014and2019 = allMergedSheet_2014and2019_onlytopDept.groupby(('入院（就诊）科室名称', '入院年份')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
deptMergedSheet_2014and2019['死亡率'] = deptMergedSheet_2014and2019['是否死亡'] / deptMergedSheet_2014and2019['患者编号']
deptMergedSheet_2014and2019.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率高的科室统计2014to2019.xlsx', encoding="UTF-8", na_rep="", index=True)




#内外科对比
inoutdeptDf = pd.read_excel(r'D:\Ynby\Doc\Demo\科室分科_内外科.xlsx', sheetname='Sheet1')
depts = np.unique(inoutdeptDf['科室'].values)
inoutdeptDict = {1 : '外科', 2: '内科', 3: '其他'}
staydays_dept_ztest_mean = np.zeros((len(depts), len(depts)))
staydays_dept_ztest_p = np.zeros((len(depts), len(depts)))
death_dept_ztest_mean = np.zeros((len(depts), len(depts)))
death_dept_ztest_p = np.zeros((len(depts), len(depts)))

all_staydays_year_ztest_p = []
all_death_year_ztest_p= []

allMergedSheet = pd.merge(allMergedSheet, inoutdeptDf, on='入院（就诊）科室名称')
for deptId in range(len(depts)):
    #年份变化
    eachDeptMergedSheet = allMergedSheet[allMergedSheet['科室'] == depts[deptId]]
    years = np.unique(eachDeptMergedSheet['入院年份'])
    if len(years) < 2019-2014+1:
        continue
    years = [2014, 2019]

    staydays_year_ztest_mean = np.zeros((len(years), len(years)))
    staydays_year_ztest_p = np.zeros((len(years), len(years)))
    death_year_ztest_mean = np.zeros((len(years), len(years)))
    death_year_ztest_p = np.zeros((len(years), len(years)))

    for rowyearId in range(len(years)):
        for colyearId in range(len(years)):
            list1= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[rowyearId]]['住院天数'].values
            list1 = list1[np.isnan(list1) == False]
            list2= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[colyearId]]['住院天数'].values
            list2 = list2[np.isnan(list2) == False]
            ztest = sw.ztest(list1, list2)
            staydays_year_ztest_mean[rowyearId, colyearId] = ztest[0]
            staydays_year_ztest_p[rowyearId, colyearId] = ztest[1]

            list1= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[rowyearId]]['是否死亡'].values
            list1 = list1[np.isnan(list1) == False]
            list2= eachDeptMergedSheet[eachDeptMergedSheet['入院年份'] == years[colyearId]]['是否死亡'].values
            list2 = list2[np.isnan(list2) == False]
            ztest = sw.ztest(list1, list2)
            death_year_ztest_mean[rowyearId, colyearId] = ztest[0]
            death_year_ztest_p[rowyearId, colyearId] = ztest[1]


    staydays_year_ztest_p = pd.DataFrame(staydays_year_ztest_p).iloc[0:1, 1:2]
    staydays_year_ztest_p['科室'] = depts[deptId]
    if len(all_staydays_year_ztest_p) != 0:
        all_staydays_year_ztest_p = pd.concat([all_staydays_year_ztest_p, staydays_year_ztest_p], axis=0)
    else:
        all_staydays_year_ztest_p = staydays_year_ztest_p

    death_year_ztest_p = pd.DataFrame(death_year_ztest_p).iloc[0:1, 1:2]
    death_year_ztest_p = pd.DataFrame(np.round(death_year_ztest_p, 5))
    death_year_ztest_p['科室'] = depts[deptId]
    if len(all_death_year_ztest_p) != 0:
        all_death_year_ztest_p = pd.concat([all_death_year_ztest_p, death_year_ztest_p], axis=0)
    else:
        all_death_year_ztest_p = death_year_ztest_p

all_staydays_year_ztest_p.rename(columns={1: '住院天数p值'}, inplace=True)
all_staydays_year_ztest_p.sort_values(by='住院天数p值', ascending=True, inplace=True)
all_death_year_ztest_p.rename(columns={1: '死亡率p值'}, inplace=True)
all_death_year_ztest_p.sort_values(by='死亡率p值', ascending=True, inplace=True)

inoutdeptMergedSheet = allMergedSheet.groupby('科室').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
inoutdeptMergedSheet['死亡率'] = inoutdeptMergedSheet['是否死亡'] / inoutdeptMergedSheet['患者编号']
inoutdeptMergedSheet = inoutdeptMergedSheet.sort_values(by='死亡率', ascending=False)
inoutdeptMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_内外科统计.xlsx', encoding="UTF-8", na_rep="", index=True)

all_staydays_year_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_住院天数_内外科2014到2019变化z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)
all_death_year_ztest_p.to_excel(r'D:\Ynby\Doc\Demo/住院数据_死亡率_内外科2014到2019变化z检验的p值.xlsx', encoding="UTF-8", na_rep="", index=True)




#内外科按月份对比
monthlyinoutDeptMergedSheet = allMergedSheet.groupby(('入院月份','科室')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
monthlyinoutDeptMergedSheet['死亡率'] = monthlyinoutDeptMergedSheet['是否死亡'] / monthlyMergedSheet['患者编号']
monthlyinoutDeptMergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_内外科_入院月度统计.xlsx', encoding="UTF-8", na_rep="", index=True)

for deptId in list(inoutdeptDict.keys()):
    eachallMergedSheet = allMergedSheet[allMergedSheet['科室'] == deptId]
    eachmonthlyinoutDeptMergedSheet = eachallMergedSheet.groupby('入院月份').agg({'患者编号': 'count', '是否死亡': 'sum', '住院天数': 'mean'})
    eachmonthlyinoutDeptMergedSheet['死亡率'] = eachmonthlyinoutDeptMergedSheet['是否死亡'] / eachmonthlyinoutDeptMergedSheet['患者编号']

    fig, ax = plt.subplots()
    plt.plot(list(range(1, 13)), eachmonthlyinoutDeptMergedSheet['住院天数'].values, '-*')
    # plt.plot(list(range(len(yearmonthlyinoutDeptMergedSheet.index))), yearmonthlyinoutDeptMergedSheet['住院天数'].values,'-*')
    plt.title(inoutdeptDict[deptId] + u'按月份平均住院天数', fontproperties=zhfont1)
    plt.xlabel('月份', fontproperties=zhfont1)
    plt.ylabel('住院天数', fontproperties=zhfont1)
    plt.legend(prop=zhfont1)
    # plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
    plt.savefig(r'D:\Ynby\Doc\Demo/' + inoutdeptDict[deptId] + '按月份平均住院天数.jpg')
    plt.show()

    fig, ax = plt.subplots()
    plt.plot(list(range(1, 13)), eachmonthlyinoutDeptMergedSheet['死亡率'].values, '-*')
    # plt.plot(list(range(len(yearmonthlyinoutDeptMergedSheet.index))), yearmonthlyinoutDeptMergedSheet['住院天数'].values,'-*')
    plt.title(inoutdeptDict[deptId] + u'按月份死亡率', fontproperties=zhfont1)
    plt.xlabel('月份', fontproperties=zhfont1)
    plt.ylabel('死亡率', fontproperties=zhfont1)
    plt.legend(prop=zhfont1)
    # plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
    plt.savefig(r'D:\Ynby\Doc\Demo/' + inoutdeptDict[deptId] + '按月份死亡率.jpg')
    plt.show()

