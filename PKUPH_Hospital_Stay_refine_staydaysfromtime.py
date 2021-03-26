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
outfolder = r'D:\Ynby\Doc\Demo\按出院时间维度_出入院时间'
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
                                   'EMR.就诊.就诊基本信息.出院日期' : '出院时间', '出院日期' : '出院时间', 'EMR.就诊.就诊基本信息.就诊年龄（岁）' : '就诊年龄（岁）'}, inplace=True)
        sheet_death['是否死亡'] = 1
        sheet_death = sheet_death.iloc[:, [eachcolId for eachcolId in range(len(sheet_death.columns)) if sheet_death.columns.values[eachcolId] in ['患者编号', '入院（就诊）时间', '是否死亡']]]

        mergedSheet = pd.merge(sheet_gender, sheet_hosp, on = '患者编号')
        mergedSheet = pd.merge(mergedSheet, sheet_death, on = ['患者编号', '入院（就诊）时间'], how='left')
        mergedSheet['是否死亡'][np.isnan(mergedSheet['是否死亡'])] = 0

        mergedSheet['入院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['入院（就诊）时间']]
        mergedSheet['入院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['入院（就诊）时间']]
        mergedSheet['出院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['出院时间']]
        mergedSheet['出院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['出院时间']]
        datetime_in = [datetime.datetime.strptime(eachdatetime, "%Y-%m-%d %H:%M:%S") for eachdatetime in mergedSheet['入院（就诊）时间']]
        datetime_out = [datetime.datetime.strptime(eachdatetime, "%Y-%m-%d %H:%M:%S") for eachdatetime in mergedSheet['出院时间']]
        mergedSheet['住院天数_出入院时间'] = [(datetime_out[rowId] - datetime_in[rowId]).days for rowId in range(len(mergedSheet))]
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

# allMergedSheet.to_excel(personfolder+r'/allMergedSheet.xlsx', encoding="UTF-8", na_rep="", index=True)

# wrongallMergedSheet = allMergedSheet.iloc[[rowId for rowId in range(len(allMergedSheet)) if (allMergedSheet['住院天数'].iloc[rowId] != allMergedSheet['住院天数_出入院时间'].iloc[rowId]) and (np.isnan(allMergedSheet['住院天数'].iloc[rowId]) == False)], :]


yearmonthlyMergedSheet = allMergedSheet.groupby('入院年月').agg({'患者编号':'count','是否死亡':'sum', '住院天数_出入院时间':'mean'})
yearmonthlyMergedSheet['死亡率'] = yearmonthlyMergedSheet['是否死亡'] / yearmonthlyMergedSheet['患者编号']
yearmonthlyMergedSheet.to_excel(outfolder+r'/住院数据_入院年月统计_出入院时间.xlsx', encoding="UTF-8", na_rep="", index=True)
yearmonthlyMergedSheet.to_csv(outfolder+r'/住院数据_入院年月统计_出入院时间.csv', encoding="UTF-8", na_rep="", index=True)


fig, ax = plt.subplots()
ax.set_xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54], minor=False)
ax.xaxis.grid(True, which='major', linewidth=2)
plt.plot(list(range(len(yearmonthlyMergedSheet.index))), yearmonthlyMergedSheet['住院天数_出入院时间'].values,'-*')
plt.title(u'2014-2019每月平均住院天数', fontproperties=zhfont1)
plt.xlabel('年月', fontproperties=zhfont1)
plt.ylabel('住院天数', fontproperties=zhfont1)
plt.legend(prop=zhfont1)
plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
plt.savefig(outfolder+r'/2014-2019每月平均住院天数.jpg')
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
plt.savefig(outfolder + r'/2014-2019每月死亡率.jpg')
plt.show()
