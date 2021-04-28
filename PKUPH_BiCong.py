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
import datetime
import scipy
import statsmodels.stats.weightstats as sw
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pymysql
import jieba
import re
import paddle
import jieba.lac_small
from collections import Counter

# 百度词法分析
# https://ai.baidu.com/ai-doc/NLP/fk6z52f2u
# https://ai.baidu.com/forum/topic/show/496975

def is_number(num):
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(num)
    if result:
        return True
    else:
        return False


zhfont1 = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=20)

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# https://mimic.physionet.org/
# 3、EMR.病史(含查体).xlsx ： 现病史， 既往史， 家族史（遗传病）， 查体（包括血压等），
# 4、EMR.诊断.xlsx  诊断名称
# 11、EMR.其他_生命体征.xlsx 身高， 体重（第一次），

pattern = r' |,|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|（|）|：|”|“'
sepcharacter = [',', '\.', '/', ';', '\'', "|", "[", "]", "<", ">", "?", ": ", "{", "}", "~", "!", "@", "#", "$", '%', '^', '&', '(', ')', '-', '=', '_', '+', '，', '。', '、', '；', '‘', '（','）','：','”', '“', ":"]


def Text2Class(allDf, colname, useregex=True):
    #分类型变量数字化
    DiagnoseTypes = []

    if useregex == True:
        for rowId in range(len(allDf)):
            if allDf[colname].iloc[rowId] is not np.nan:
                result_list = re.split(pattern, allDf[colname].iloc[rowId])
                DiagnoseTypes = DiagnoseTypes + result_list
    else:
        for rowId in range(len(allDf)):
            if allDf[colname].iloc[rowId] is not np.nan:
                result_list = allDf[colname].iloc[rowId]
                DiagnoseTypes = DiagnoseTypes + [result_list]

    DiagnoseTypeCount = pd.Series(DiagnoseTypes).value_counts()
    if useregex == True:
        DiagnoseTypeCount = DiagnoseTypeCount[DiagnoseTypeCount.index.values > '9']
    DiagnoseTypeCount = DiagnoseTypeCount[DiagnoseTypeCount > 5]

    for eachDiagnoseColId in range(len(DiagnoseTypeCount)):
        allDf[colname + '_' + str(DiagnoseTypeCount.index.values[eachDiagnoseColId])] = 0

    for eachDiagnoseColId in range(len(DiagnoseTypeCount)):
        colId = np.where(allDf.columns == colname + '_' + str(DiagnoseTypeCount.index.values[eachDiagnoseColId]))[0][0]
        for rowId in range(len(allDf)):
            if allDf[colname].iloc[rowId] is not np.nan:
                if useregex == True:
                    if allDf[colname].iloc[rowId].find(DiagnoseTypeCount.index.values[eachDiagnoseColId]) >= 0:
                        allDf.iloc[rowId, colId] = 1
                else:
                    if allDf[colname].iloc[rowId] == DiagnoseTypeCount.index.values[eachDiagnoseColId]:
                        allDf.iloc[rowId, colId] = 1

    return DiagnoseTypeCount, allDf


bicong_parent_folder = r'D:\Ynby\Doc\Demo\臂丛\臂丛/'
bicong_personData = pd.read_excel(bicong_parent_folder + '1.患者基本信息.xlsx', encoding="UTF-8", na_rep="", index=True)
bicong_personData_duplicated = bicong_personData.loc[:, ['患者编号']].duplicated()
duplicatedIndex = bicong_personData_duplicated[bicong_personData_duplicated == True].index.values
bicong_personData_duplicated = bicong_personData.loc[:, ['患者编号']].iloc[list(duplicatedIndex), :].drop_duplicates()
bicong_personData_duplicated.to_csv(r'D:\Ynby\Doc\Demo/臂丛/1.患者基本信息重复数据.csv', encoding="UTF-8", na_rep="", index=False)
bicong_personData_duplicated.to_excel(r'D:\Ynby\Doc\Demo/臂丛/1.患者基本信息重复数据.xlsx', encoding="UTF-8", na_rep="", index=False)
# bicong_personData = bicong_personData.groupby(by=('患者编号')).apply(lambda t: t[t.就诊次数==t.就诊次数.min()])
# bicong_personData.drop(['患者编号'], axis=1, inplace=True)
# bicong_personData.reset_index(inplace=True)
# bicong_personData.drop(['level_1'], axis=1, inplace=True)


bicong_jiuzhenData = pd.read_excel(bicong_parent_folder + '2.就诊基本信息.xlsx', encoding="UTF-8", na_rep="", index=True)
bicong_jiuzhenData_duplicated = bicong_jiuzhenData.loc[:, ['患者编号', '就诊次数']].duplicated()
duplicatedIndex = bicong_jiuzhenData_duplicated[bicong_jiuzhenData_duplicated == True].index.values
bicong_jiuzhenData_duplicated = bicong_jiuzhenData.loc[:, ['患者编号', '就诊次数']].iloc[list(duplicatedIndex), :]
bicong_jiuzhenData_duplicated.to_csv(r'D:\Ynby\Doc\Demo/臂丛/2.就诊基本信息重复数据.csv', encoding="UTF-8", na_rep="", index=False)
bicong_jiuzhenData_duplicated.to_excel(r'D:\Ynby\Doc\Demo/臂丛/2.就诊基本信息重复数据.xlsx', encoding="UTF-8", na_rep="", index=False)
bicong_jiuzhenData_unique = bicong_jiuzhenData.iloc[[rowId for rowId in range(len(bicong_jiuzhenData)) if rowId not in duplicatedIndex], :]
bicong_Data = pd.merge(bicong_personData, bicong_jiuzhenData_unique.iloc[:, list(range(2)) + list(range(3, len(bicong_jiuzhenData_unique.columns)))], on=('患者编号', '就诊次数'))

bicong_BingShiData = pd.read_excel(bicong_parent_folder + '3.病史.xlsx', encoding="UTF-8", na_rep="", index=True)
bicong_BingshiData_duplicated = bicong_BingShiData.loc[:, ['患者编号', '就诊次数']].duplicated()
duplicatedIndex = bicong_BingshiData_duplicated[bicong_BingshiData_duplicated == True].index.values
bicong_BingshiData_duplicated = bicong_BingShiData.loc[:, ['患者编号', '就诊次数']].iloc[list(duplicatedIndex), :]
bicong_BingshiData_duplicated.to_csv(r'D:\Ynby\Doc\Demo/臂丛/3.病史重复数据.csv', encoding="UTF-8", na_rep="", index=False)
bicong_BingshiData_duplicated.to_excel(r'D:\Ynby\Doc\Demo/臂丛/3.病史重复数据.xlsx', encoding="UTF-8", na_rep="", index=False)
bicong_BingshiData_unique = bicong_BingShiData.iloc[[rowId for rowId in range(len(bicong_BingShiData)) if rowId not in duplicatedIndex], :]
bicong_Data = pd.merge(bicong_Data, bicong_BingshiData_unique, on=('患者编号', '就诊次数'))
# bicong_Data = pd.merge(bicong_Data, bicong_BingshiData_unique, on=('患者编号', '就诊次数'), how='left')


bicong_zhenduanData = pd.read_excel(bicong_parent_folder + '4.诊断.xlsx', encoding="UTF-8", na_rep="", index=True)
bicong_zhenduanData_duplicated = bicong_zhenduanData.loc[:, ['患者编号', '就诊次数']].duplicated()
duplicatedIndex = bicong_zhenduanData_duplicated[bicong_zhenduanData_duplicated == True].index.values
bicong_zhenduanData_duplicated = bicong_zhenduanData.loc[:, ['患者编号', '就诊次数']].iloc[list(duplicatedIndex), :]
bicong_zhenduanData_duplicated.to_csv(r'D:\Ynby\Doc\Demo/臂丛/4.诊断重复数据.csv', encoding="UTF-8", na_rep="", index=False)
bicong_zhenduanData_duplicated.to_excel(r'D:\Ynby\Doc\Demo/臂丛/4.诊断重复数据.xlsx', encoding="UTF-8", na_rep="", index=False)
bicong_zhenduanData_unique = bicong_zhenduanData.iloc[[rowId for rowId in range(len(bicong_zhenduanData)) if rowId not in duplicatedIndex], :]
bicong_Data = pd.merge(bicong_Data, bicong_zhenduanData_unique, on=('患者编号', '就诊次数'), how='left')


bicong_shengmingtizhengData = pd.read_excel(bicong_parent_folder + '11.生命体征.xlsx', encoding="UTF-8", na_rep="", index=True)
# bicong_shengmingtizhengData = bicong_shengmingtizhengData.groupby(by=('患者编号','项目名称')).apply(lambda t: t[t.就诊次数==t.就诊次数.min()])
# bicong_shengmingtizhengData.drop(['患者编号','项目名称'], axis=1, inplace=True)
# bicong_shengmingtizhengData.reset_index(inplace=True)
# bicong_shengmingtizhengData.drop(['level_2'], axis=1, inplace=True)
bicong_shenmingtizhengData_duplicated = bicong_shengmingtizhengData.loc[:, ['患者编号', '就诊次数','项目名称']].duplicated()
duplicatedIndex = bicong_shenmingtizhengData_duplicated[bicong_shenmingtizhengData_duplicated == True].index.values
bicong_shenmingtizhengData_duplicated = bicong_shengmingtizhengData.loc[:, ['患者编号', '就诊次数','项目名称']].iloc[list(duplicatedIndex), :].drop_duplicates()
bicong_shenmingtizhengData_duplicated.to_csv(r'D:\Ynby\Doc\Demo/臂丛/11.生命体征重复数据.csv', encoding="UTF-8", na_rep="", index=False)
bicong_shenmingtizhengData_duplicated.to_excel(r'D:\Ynby\Doc\Demo/臂丛/11.生命体征重复数据.xlsx', encoding="UTF-8", na_rep="", index=False)
bicong_shenmingtizhengData_unique = bicong_shengmingtizhengData.iloc[[rowId for rowId in range(len(bicong_shengmingtizhengData)) if rowId not in duplicatedIndex], :]


NewColumns = ['体重', '身高', '收缩压', '舒张压']
bicong_ItemData = bicong_shenmingtizhengData_unique.loc[:, ['患者编号', '就诊次数']].drop_duplicates()
for eachColumn in NewColumns:
    bicong_ItemData[eachColumn] = np.nan

for rowId in range(len(bicong_ItemData)):
    for colId in range(len(NewColumns)):
        eachcol = NewColumns[colId]
        set1 = set(list(np.where(bicong_shenmingtizhengData_unique['患者编号'] == bicong_ItemData['患者编号'].iloc[rowId])[0]))
        set2 = set(list(np.where(bicong_shenmingtizhengData_unique['项目名称'] == eachcol)[0]))
        if len(list(set.intersection(set1, set2))) > 0:
            bicong_ItemData.iloc[rowId, colId+2] = bicong_shenmingtizhengData_unique.iloc[list(set.intersection(set1, set2))[0], 3]

bicong_Data = pd.merge(bicong_Data, bicong_ItemData, on=('患者编号', '就诊次数'), how='left')

bicong_Data = bicong_Data.sort_values(by='体重', ascending=True)
bicong_Data_duplicated = bicong_Data.loc[:, ['患者编号']].duplicated()
duplicatedIndex = bicong_Data_duplicated[bicong_Data_duplicated == True].index.values
bicong_Data_unique = bicong_Data.iloc[[rowId for rowId in range(len(bicong_Data)) if rowId not in duplicatedIndex], :]

bicong_Data_unique.to_csv(r'D:\Ynby\Doc\Demo/臂丛/臂丛数据.csv', encoding="UTF-8", na_rep="", index=False)
bicong_Data_unique.to_excel(r'D:\Ynby\Doc\Demo/臂丛/臂丛数据.xlsx', encoding="UTF-8", na_rep="", index=False)



