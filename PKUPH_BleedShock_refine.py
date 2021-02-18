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

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


BleedShock_Df=pd.read_excel(r'D:\Ynby\Doc\Demo/出血性休克数据11.24_列名去空格.xlsx')

#去除重复列
for colId in range(BleedShock_Df.shape[1]-1, -1, -1):
    if type(BleedShock_Df.columns.values[colId]) == type('s'):
        if BleedShock_Df.columns.values[colId].find('.1') > 0:
            print(colId, BleedShock_Df.columns.values[colId])
for colId in range(BleedShock_Df.shape[1] - 1, -1, -1):
    if type(BleedShock_Df.columns.values[colId]) == type('s'):
        if BleedShock_Df.columns.values[colId].find('.2') > 0:
            print(colId, BleedShock_Df.columns.values[colId])
for colId in range(BleedShock_Df.shape[1] - 1, -1, -1):
    if type(BleedShock_Df.columns.values[colId]) == type('s'):
        if BleedShock_Df.columns.values[colId].find('.3') > 0:
            print(colId, BleedShock_Df.columns.values[colId])
for colId in range(BleedShock_Df.shape[1] - 1, -1, -1):
    if type(BleedShock_Df.columns.values[colId]) == type('s'):
        if BleedShock_Df.columns.values[colId].find('.4') > 0:
            print(colId, BleedShock_Df.columns.values[colId])


int64colIds = []
int64colNamess = []
for colId in range(len(BleedShock_Df.columns)):
    if BleedShock_Df.dtypes[colId] == np.dtype('int64'):
        int64colIds = int64colIds + [colId]
        int64colNamess = int64colIds + [BleedShock_Df.columns[colId]]
        print(colId, BleedShock_Df.columns[colId], BleedShock_Df.dtypes[colId])

float64colIds = []
float64colNamess = []
for colId in range(len(BleedShock_Df.columns)):
    if BleedShock_Df.dtypes[colId] == np.dtype('float64'):
        float64colIds = float64colIds + [colId]
        float64colNamess = float64colNamess + [BleedShock_Df.columns[colId]]
        print(colId, BleedShock_Df.columns[colId], BleedShock_Df.dtypes[colId])

objectcolIds = []
objectcolNamess = []
for colId in range(len(BleedShock_Df.columns)):
    if BleedShock_Df.dtypes[colId] == np.dtype('O'):
        objectcolIds = objectcolIds + [colId]
        objectcolNamess = objectcolNamess + [BleedShock_Df.columns[colId]]
        print(colId, BleedShock_Df.columns[colId], BleedShock_Df.dtypes[colId])

shouldBeStrColNames = [eachColName.replace(" ", "") for eachColName in ['病史ID', '性别', '出院诊断', '主诉', '现病史', '主要出血部位', '手术名称', '血管活性药物去甲肾上腺素1、多巴胺2、肾上腺素3、间羟胺4、异丙肾5', '感染部位']]

YesNoColNames = ['抗凝药及抗血小板药史', '当前吸烟', '当前饮酒', '过敏史']
for eachcolId in range(len(YesNoColNames)):
    colId = np.where(BleedShock_Df.columns == YesNoColNames[eachcolId])[0][0]
    for rowId in range(len(BleedShock_Df)):
        if BleedShock_Df.iloc[rowId, colId] == '是':
            BleedShock_Df.iloc[rowId, colId] = 1
        elif BleedShock_Df.iloc[rowId, colId] == '否':
            BleedShock_Df.iloc[rowId, colId] = 0

for eachcolId in range(len(YesNoColNames)):
    BleedShock_Df[YesNoColNames[eachcolId]] = BleedShock_Df[YesNoColNames[eachcolId]].astype(int)

hourColNames = ['入院到手术时间h', '使用时间h']
for hourColId in range(len(hourColNames)):
    colId = np.where(BleedShock_Df.columns == hourColNames[hourColId])[0][0]
    for rowId in range(len(BleedShock_Df)):
        if type(BleedShock_Df.iloc[rowId, colId]) == type('s'):
            if BleedShock_Df.iloc[rowId, colId].find("d") > 0:
                BleedShock_Df.iloc[rowId, colId] = int(BleedShock_Df.iloc[rowId, colId].split("d")[0])*24
    BleedShock_Df[hourColNames[hourColId]] = BleedShock_Df[hourColNames[hourColId]].astype(float)


shouldBeDateColNames = [eachColName.replace(" ", "") for eachColName in ['入院时间', '手术开始时间（几点几分）', '手术结束时间', '出院时间', '入ICU时间-1', '出ICU时间-1', '开始时间', '结束时间', ]]

for eachColName in shouldBeStrColNames + shouldBeDateColNames:
    colId = np.where(BleedShock_Df.columns == eachColName)[0][0]
    BleedShock_Df[eachColName] = BleedShock_Df[eachColName].astype('str')
    for rowId in range(len(BleedShock_Df)):
        if BleedShock_Df.iloc[rowId, colId] is not np.nan:
            BleedShock_Df.iloc[rowId, colId] = BleedShock_Df.iloc[rowId, colId].strip()


BleedShock_Df.to_csv(r'D:\Ynby\Doc\Demo/出血性休克数据_清洗干净.csv', encoding="UTF-8", na_rep="")
BleedShock_Df.to_excel(r'D:\Ynby\Doc\Demo/出血性休克数据_清洗干净.xlsx', encoding="UTF-8", na_rep="")


#分类型变量数字化
import re
pattern = r' |,|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|（|）'

toBeCategorizedColnames = ['主要出血部位', '手术名称', '血管活性药物去甲肾上腺素1、多巴胺2、肾上腺素3、间羟胺4、异丙肾5', '感染部位']
for eachcolname in toBeCategorizedColnames:
    BleedParts = []
    for rowId in range(len(BleedShock_Df)):
        if BleedShock_Df[eachcolname].iloc[rowId] is not np.nan:
            if len(BleedShock_Df[eachcolname].iloc[rowId]) > 0:
                if BleedShock_Df[eachcolname].iloc[rowId] != 'nan':
                    result_list = re.split(pattern, BleedShock_Df[eachcolname].iloc[rowId].replace('左','').replace('右',''))
                    BleedParts = BleedParts + result_list

    DiagnoseTypeCount = pd.Series(BleedParts).value_counts()
    DiagnoseTypeCount = DiagnoseTypeCount[DiagnoseTypeCount > len(BleedParts)*0.02]
    DiagnoseTypeCount = DiagnoseTypeCount[DiagnoseTypeCount.index.values != '']
    DiagnoseTypeCount = DiagnoseTypeCount[DiagnoseTypeCount.index.values > '9']

    for eachDiagnoseColId in range(len(DiagnoseTypeCount)):
        BleedShock_Df[DiagnoseTypeCount.index.values[eachDiagnoseColId]] = 0

    for eachDiagnoseColId in range(len(DiagnoseTypeCount)):
        colId = np.where(BleedShock_Df.columns == DiagnoseTypeCount.index.values[eachDiagnoseColId])[0][0]
        for rowId in range(len(BleedShock_Df)):
            if BleedShock_Df[eachcolname].iloc[rowId].find(DiagnoseTypeCount.index.values[eachDiagnoseColId]) > 0:
                BleedShock_Df.iloc[rowId, colId] = 1


BleedShock_Df['出院转归类别'] = np.nan
colId = np.where(BleedShock_Df.columns == '出院转归类别')[0][0]
RecoveryTypeDict = {'医嘱离院':0, "医嘱转院":1, "死亡":2}
for rowId in range(len(BleedShock_Df)):
    if BleedShock_Df['出院转归'][rowId] == '医嘱离院':
        BleedShock_Df.iloc[rowId, colId] = 0
    elif BleedShock_Df['出院转归'][rowId] == "医嘱转院":
        BleedShock_Df.iloc[rowId, colId] = 1
    elif BleedShock_Df['出院转归'][rowId] == "死亡":
        BleedShock_Df.iloc[rowId, colId] = 2

BleedShock_Df.to_csv(r'D:\Ynby\Doc\Demo/出血性休克数据_清洗干净_分类.csv', encoding="UTF-8", na_rep="", index=False)
BleedShock_Df.to_excel(r'D:\Ynby\Doc\Demo/出血性休克数据_清洗干净_分类.xlsx', encoding="UTF-8", na_rep="", index=False)





