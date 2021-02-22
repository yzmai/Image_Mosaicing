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

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


parent_folder = r'D:\Ynby\Doc\Demo\王储final'
hospital_in_list = os.listdir(parent_folder)

calendarData = calendar.get_all_calendar()
holidayDict = {'工作日非周末' : 0, '工作日周末' : 1, '休息日周末' : 2, '休息日节假日' : 3}
# holidayDict = {'weekday' : 0, 'workingweekend' : 1, 'normalweekend' : 2, 'holiday' : 3}
calendarData['工作日周末节假'] = np.nan
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 1)[0]), set(np.where(calendarData['isholiday'] == 'Y')[0])))] = 3
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 0)[0]), set(np.where(calendarData['isholiday'] == 'Y')[0])))] = 2
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 2)[0]), set(np.where(calendarData['isholiday'] == 'N')[0])))] = 1
calendarData['工作日周末节假'].iloc[list(set.intersection(set(np.where(calendarData['status'] == 0)[0]), set(np.where(calendarData['isholiday'] == 'N')[0])))] = 0
calendarData['工作日周末节假'] = calendarData['工作日周末节假'].astype(np.int16)
calendarData['date'] = [datetime.datetime.strftime(eachstr, "%Y-%m-%d") for eachstr in calendarData['date']]

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


yearmonthlyMergedSheet = allMergedSheet.groupby('入院年月').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearmonthlyMergedSheet['死亡率'] = yearmonthlyMergedSheet['是否死亡'] / yearmonthlyMergedSheet['患者编号']
yearlyMergedSheet = allMergedSheet.groupby('入院年份').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearlyMergedSheet['死亡率'] = yearlyMergedSheet['是否死亡'] / yearlyMergedSheet['患者编号']
yearlyindeptMergedSheet = allMergedSheet.groupby(by=('入院年份', '入院（就诊）科室名称')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearlyindeptMergedSheet['死亡率'] = yearlyindeptMergedSheet['是否死亡'] / yearlyindeptMergedSheet['患者编号']
yearlyoutdeptMergedSheet = allMergedSheet.groupby(by=('入院年份', '出院科室名称')).agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
yearlyoutdeptMergedSheet['死亡率'] = yearlyoutdeptMergedSheet['是否死亡'] / yearlyoutdeptMergedSheet['患者编号']

monthlyMergedSheet = allMergedSheet.groupby('入院月份').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
monthlyMergedSheet['死亡率'] = monthlyMergedSheet['是否死亡'] / monthlyMergedSheet['患者编号']
weeklyMergedSheet = allMergedSheet.groupby('入院周几').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
weeklyMergedSheet['死亡率'] = weeklyMergedSheet['是否死亡'] / weeklyMergedSheet['患者编号']
hourlyMergedSheet = allMergedSheet.groupby('入院小时').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
hourlyMergedSheet['死亡率'] = hourlyMergedSheet['是否死亡'] / hourlyMergedSheet['患者编号']
weekdayendholidayMergedSheet = allMergedSheet.groupby('入院工作日周末节假').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
weekdayendholidayMergedSheet['死亡率'] = weekdayendholidayMergedSheet['是否死亡'] / weekdayendholidayMergedSheet['患者编号']

genderMergedSheet = allMergedSheet.groupby('性别').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
genderMergedSheet['死亡率'] = genderMergedSheet['是否死亡'] / genderMergedSheet['患者编号']

ageMergedSheet = allMergedSheet.groupby('就诊年龄（岁）').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
ageMergedSheet['死亡率'] = ageMergedSheet['是否死亡'] / ageMergedSheet['患者编号']
ageMergedSheet = ageMergedSheet.sort_values(by='死亡率', ascending=False)

deptMergedSheet = allMergedSheet.groupby('入院（就诊）科室名称').agg({'患者编号':'count','是否死亡':'sum', '住院天数':'mean'})
deptMergedSheet['死亡率'] = deptMergedSheet['是否死亡'] / deptMergedSheet['患者编号']
deptMergedSheet = deptMergedSheet.sort_values(by='死亡率', ascending=False)

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




mergedSheet.to_csv(r'D:\Ynby\Doc\Demo/住院数据_已清洗_二分类.csv', encoding="UTF-8", na_rep="", index=False)
mergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_已清洗_二分类.xlsx', encoding="UTF-8", na_rep="", index=False)


