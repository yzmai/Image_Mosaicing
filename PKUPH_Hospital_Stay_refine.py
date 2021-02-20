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

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


parent_folder = r'D:\Ynby\Doc\Demo\王储final'
hospital_in_list = os.listdir(parent_folder)

calendarData = calendar.get_all_calendar()

for filename in hospital_in_list:
    if filename.find('201') >= 0:
        b = xlrd.open_workbook(os.path.join(parent_folder, filename))
        sheet_gender = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[0].name)
        sheet_hosp = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[1].name)
        sheet_death = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[2].name)
        sheet_death['是否死亡'] = 1
        sheet_death = sheet_death.iloc[:, [eachcolId for eachcolId in range(len(sheet_death.columns)) if sheet_death.columns.values[eachcolId] in ['患者编号', '入院（就诊）时间', '是否死亡']]]

        mergedSheet = pd.merge(sheet_gender, sheet_hosp, on = '患者编号')
        mergedSheet = pd.merge(mergedSheet, sheet_death, on = ['患者编号', '入院（就诊）时间'], how='left')
        mergedSheet['是否死亡'][np.isnan(mergedSheet['是否死亡'])] = 0

        mergedSheet['入院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['入院（就诊）时间']]
        mergedSheet['入院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['入院（就诊）时间']]
        mergedSheet['出院Date'] = [eachstr.split(' ')[0] for eachstr in mergedSheet['出院日期']]
        mergedSheet['出院Time'] = [eachstr.split(' ')[1] for eachstr in mergedSheet['出院日期']]



#Calenda节日假期等

mergedSheet.to_csv(r'D:\Ynby\Doc\Demo/住院数据_已清洗_二分类.csv', encoding="UTF-8", na_rep="", index=False)

mergedSheet.to_excel(r'D:\Ynby\Doc\Demo/住院数据_已清洗_二分类.xlsx', encoding="UTF-8", na_rep="", index=False)


