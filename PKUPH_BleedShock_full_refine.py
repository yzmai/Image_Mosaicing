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
import re
import datetime

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


parent_folder = r'D:\Ynby\Doc\Demo\王储final'
pattern = r' |,|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|（|）'


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
    DiagnoseTypeCount = DiagnoseTypeCount[DiagnoseTypeCount > 30]

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

    return allDf



allMergedSheet = []
filename = r'D:\Ynby\Doc\Demo/出血性休克院前+院内(脱敏)2.19_已清洗.xlsx'
b = xlrd.open_workbook(filename)
sheet_yuanqian = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[0].name)

sheet_yuanqian = Text2Class(sheet_yuanqian, 'MPDS症状')
sheet_yuanqian = Text2Class(sheet_yuanqian, 'TI部位')
sheet_yuanqian = Text2Class(sheet_yuanqian, 'TI创伤类型')

colname = '预警级别'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '轻度':
        sheet_yuanqian.iloc[rowId, colId] = 0
    elif sheet_yuanqian[colname].iloc[rowId] == '中度':
        sheet_yuanqian.iloc[rowId, colId] = 1
    elif sheet_yuanqian[colname].iloc[rowId] == '重度':
        sheet_yuanqian.iloc[rowId, colId] = 2

colname = '预警级别'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '轻度':
        sheet_yuanqian.iloc[rowId, colId] = 0
    elif sheet_yuanqian[colname].iloc[rowId] == '中度':
        sheet_yuanqian.iloc[rowId, colId] = 1
    elif sheet_yuanqian[colname].iloc[rowId] == '重度':
        sheet_yuanqian.iloc[rowId, colId] = 2

colname = 'TI血压'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '<60mmHg':
        sheet_yuanqian.iloc[rowId, colId] = 0
    elif sheet_yuanqian[colname].iloc[rowId] == '60-90mmHg':
        sheet_yuanqian.iloc[rowId, colId] = 1
    elif sheet_yuanqian[colname].iloc[rowId] == '>90mmHg':
        sheet_yuanqian.iloc[rowId, colId] = 2

colname = 'TI脉搏'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '50-99次/分':
        sheet_yuanqian.iloc[rowId, colId] = 0
    elif sheet_yuanqian[colname].iloc[rowId] == '100-140次/分':
        sheet_yuanqian.iloc[rowId, colId] = 1

colname = 'TI开放伤/外出血'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '是':
        sheet_yuanqian.iloc[rowId, colId] = 1
    elif sheet_yuanqian[colname].iloc[rowId] == '否':
        sheet_yuanqian.iloc[rowId, colId] = 0

colname = 'GCS睁眼'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '自发睁眼':
        sheet_yuanqian.iloc[rowId, colId] = 0
    elif sheet_yuanqian[colname].iloc[rowId] == '语言吩咐睁眼':
        sheet_yuanqian.iloc[rowId, colId] = 1
    elif sheet_yuanqian[colname].iloc[rowId] == '疼痛刺激睁眼':
        sheet_yuanqian.iloc[rowId, colId] = 2
    elif sheet_yuanqian[colname].iloc[rowId] == '无睁眼':
        sheet_yuanqian.iloc[rowId, colId] = 3

colname = 'GCS语言'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '正常交谈':
        sheet_yuanqian.iloc[rowId, colId] = 0
    elif sheet_yuanqian[colname].iloc[rowId] == '只能说出（不适当）单词':
        sheet_yuanqian.iloc[rowId, colId] = 1
    elif sheet_yuanqian[colname].iloc[rowId] == '语言错乱':
        sheet_yuanqian.iloc[rowId, colId] = 2
    elif sheet_yuanqian[colname].iloc[rowId] == '只能发音':
        sheet_yuanqian.iloc[rowId, colId] = 3
    elif sheet_yuanqian[colname].iloc[rowId] == '无发音':
        sheet_yuanqian.iloc[rowId, colId] = 4


colname = 'GCS运动'
colId = np.where(sheet_yuanqian.columns == colname)[0][0]
for rowId in range(len(sheet_yuanqian)):
    if sheet_yuanqian[colname].iloc[rowId] is np.nan:
        continue
    if sheet_yuanqian[colname].iloc[rowId] == '按吩咐运动':
        sheet_yuanqian.iloc[rowId, colId] = 0
    elif sheet_yuanqian[colname].iloc[rowId] in  ['异常伸展', '异常屈曲']:
        sheet_yuanqian.iloc[rowId, colId] = 1
    elif sheet_yuanqian[colname].iloc[rowId] in ['对疼痛刺激定位反应', '对疼痛刺激屈曲反应']:
        sheet_yuanqian.iloc[rowId, colId] = 2
    elif sheet_yuanqian[colname].iloc[rowId] == '无反应':
        sheet_yuanqian.iloc[rowId, colId] = 3


colnames = ['瞳孔','光反射','意识','气道','循环','心率','胸部','腹部','肠鸣','肌力','骨折','体格检查其他描述']
bodyCheckDict = {'瞳孔':'正常','光反射':'正常','意识':'正常','气道':'通畅','循环':'正常','心率':'齐','胸部':'正常','腹部':'正常','肠鸣':'正常','肌力':'正常','骨折':'无','体格检查其他描述':'正常'}
Newcolnames = ['体格检查_' + eachstr for eachstr in  ['瞳孔','光反射','意识','气道','循环','心率','胸部','腹部','肠鸣','肌力','骨折','体格检查其他描述']]
colname = '体格检查'
for newcolId in range(len(Newcolnames)):
    sheet_yuanqian[Newcolnames[newcolId]] = np.nan
    colId = np.where(sheet_yuanqian.columns == Newcolnames[newcolId])[0][0]
    for rowId in range(len(sheet_yuanqian)):
        if sheet_yuanqian[colname].iloc[rowId] is np.nan:
            continue
        if sheet_yuanqian[colname].iloc[rowId].find(colnames[newcolId]+':' + bodyCheckDict[colnames[newcolId]]) >= 0:
            sheet_yuanqian.iloc[rowId, colId] = 0
        else:
            sheet_yuanqian.iloc[rowId, colId] = 1

sheet_yuanqian.to_excel(r'D:\Ynby\Doc\Demo/出血性休克_已清洗_院前急救信息_0219.xlsx', encoding="UTF-8", na_rep="", index=False)


#Sheet 2
sheet_jibenxinxi = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[1].name)
sheet_jibenxinxi.iloc[:, 0].value_counts()

colname = '性别'
colId = np.where(sheet_jibenxinxi.columns == colname)[0][0]
for rowId in range(len(sheet_jibenxinxi)):
    if sheet_jibenxinxi[colname].iloc[rowId] is np.nan:
        continue
    if sheet_jibenxinxi[colname].iloc[rowId] == '男':
        sheet_jibenxinxi.iloc[rowId, colId] = 1
    elif sheet_jibenxinxi[colname].iloc[rowId] == '女':
        sheet_jibenxinxi.iloc[rowId, colId] = 2

allMergedBleedShockDf = pd.merge(sheet_jibenxinxi, sheet_yuanqian, on ='患者ID', how='left')


#Sheet 3
sheet_bingshi = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[2].name)
sheet_bingshi = Text2Class(sheet_bingshi, '入院科室')
sheet_bingshi = Text2Class(sheet_bingshi, '既往合并症')

colname = '抗凝药及抗血小板药史'
colId = np.where(sheet_bingshi.columns == colname)[0][0]
for rowId in range(len(sheet_bingshi)):
    if sheet_bingshi[colname].iloc[rowId] is np.nan:
        continue
    if sheet_bingshi[colname].iloc[rowId] == '否':
        sheet_bingshi.iloc[rowId, colId] = 0
    elif sheet_bingshi[colname].iloc[rowId] == '是':
        sheet_bingshi.iloc[rowId, colId] = 1


colname = '当前吸烟'
colId = np.where(sheet_bingshi.columns == colname)[0][0]
for rowId in range(len(sheet_bingshi)):
    if sheet_bingshi[colname].iloc[rowId] is np.nan:
        continue
    if sheet_bingshi[colname].iloc[rowId] == '否':
        sheet_bingshi.iloc[rowId, colId] = 0
    elif sheet_bingshi[colname].iloc[rowId] == '是':
        sheet_bingshi.iloc[rowId, colId] = 1

colname = '当前饮酒'
colId = np.where(sheet_bingshi.columns == colname)[0][0]
for rowId in range(len(sheet_bingshi)):
    if sheet_bingshi[colname].iloc[rowId] is np.nan:
        continue
    if sheet_bingshi[colname].iloc[rowId] == '否':
        sheet_bingshi.iloc[rowId, colId] = 0
    elif sheet_bingshi[colname].iloc[rowId] == '是':
        sheet_bingshi.iloc[rowId, colId] = 1

colname = '过敏史'
colId = np.where(sheet_bingshi.columns == colname)[0][0]
for rowId in range(len(sheet_bingshi)):
    if sheet_bingshi[colname].iloc[rowId] is np.nan:
        continue
    if sheet_bingshi[colname].iloc[rowId] == '否':
        sheet_bingshi.iloc[rowId, colId] = 0
    elif sheet_bingshi[colname].iloc[rowId] == '是':
        sheet_bingshi.iloc[rowId, colId] = 1

colname = '预防接种史'
colId = np.where(sheet_bingshi.columns == colname)[0][0]
for rowId in range(len(sheet_bingshi)):
    if sheet_bingshi[colname].iloc[rowId] is np.nan:
        continue
    if sheet_bingshi[colname].iloc[rowId] == '否':
        sheet_bingshi.iloc[rowId, colId] = 0
    elif sheet_bingshi[colname].iloc[rowId] == '是':
        sheet_bingshi.iloc[rowId, colId] = 1

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_bingshi, on ='病史ID', how='left')


#Sheet 4
sheet_shouyeshoushuxinxi = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[3].name)
sheet_shouyeshoushuxinxi_norm = sheet_shouyeshoushuxinxi.iloc[:, 0:2].drop_duplicates()
sheet_shouyeshoushuxinxi = Text2Class(sheet_shouyeshoushuxinxi, '手术名称')

colIds= [id for id in range(len(sheet_shouyeshoushuxinxi.columns)) if sheet_shouyeshoushuxinxi.columns[id].find('手术名称_') >= 0]
df = sheet_shouyeshoushuxinxi.iloc[:, colIds].groupby(sheet_shouyeshoushuxinxi['病史ID']).apply(sum, axis=0)
df.reset_index(drop=False, inplace=True)
sheet_shouyeshoushuxinxi_norm = pd.merge(sheet_shouyeshoushuxinxi_norm, df, on='病史ID')

sheet_shouyeshoushuxinxi = Text2Class(sheet_shouyeshoushuxinxi, '麻醉方式')
colIds= [id for id in range(len(sheet_shouyeshoushuxinxi.columns)) if sheet_shouyeshoushuxinxi.columns[id].find('麻醉方式_') >= 0]
df = sheet_shouyeshoushuxinxi.iloc[:, colIds].groupby(sheet_shouyeshoushuxinxi['病史ID']).apply(sum, axis=0)
df.reset_index(drop=False, inplace=True)
sheet_shouyeshoushuxinxi_norm = pd.merge(sheet_shouyeshoushuxinxi_norm, df, on='病史ID')

sheet_shouyeshoushuxinxi = Text2Class(sheet_shouyeshoushuxinxi, '手术级别')
colIds= [id for id in range(len(sheet_shouyeshoushuxinxi.columns)) if sheet_shouyeshoushuxinxi.columns[id].find('手术级别_') >= 0]
df = sheet_shouyeshoushuxinxi.iloc[:, colIds].groupby(sheet_shouyeshoushuxinxi['病史ID']).apply(sum, axis=0)
df.reset_index(drop=False, inplace=True)
sheet_shouyeshoushuxinxi_norm = pd.merge(sheet_shouyeshoushuxinxi_norm, df, on='病史ID')

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_shouyeshoushuxinxi_norm, on ='病史ID', how='left')


#Sheet 5
sheet_shoumaxinxi = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[4].name)
colIds = [3, 4]
sheet_shoumaxinxi = sheet_shoumaxinxi.iloc[:, colIds].groupby(sheet_shoumaxinxi['病史ID']).apply(sum, axis=0)
sheet_shoumaxinxi.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_shoumaxinxi, on ='病史ID', how='left')


#Sheet 6
sheet_xuezhipinshiyong = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[5].name)
colIds = [1, 2]
sheet_xuezhipinshiyong = sheet_xuezhipinshiyong.iloc[:, colIds].groupby(sheet_xuezhipinshiyong['病史ID']).apply(sum, axis=0)
sheet_xuezhipinshiyong.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_xuezhipinshiyong, on ='病史ID', how='left')

#Sheet 7
sheet_renxianweidanbaiyuan = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[6].name)
colIds = 3
zeroRowIds = [rowId for rowId in range(len(sheet_renxianweidanbaiyuan)) if np.isnan(sheet_renxianweidanbaiyuan.iloc[rowId, colIds]) == True]
sheet_renxianweidanbaiyuan.iloc[zeroRowIds, colIds] = 0
sheet_renxianweidanbaiyuan = sheet_renxianweidanbaiyuan.iloc[:, colIds:(colIds+1)].groupby(sheet_renxianweidanbaiyuan['病史ID']).apply(sum, axis=0)
sheet_renxianweidanbaiyuan.rename(columns={'医嘱剂量' : '人纤维蛋白原_医嘱剂量'}, inplace=True)
sheet_renxianweidanbaiyuan.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_renxianweidanbaiyuan, on ='病史ID', how='left')

#Sheet 8
sheet_ningxuemeiyuan = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[7].name)
colIds = 3
zeroRowIds = [rowId for rowId in range(len(sheet_ningxuemeiyuan)) if np.isnan(sheet_ningxuemeiyuan.iloc[rowId, colIds]) == True]
sheet_ningxuemeiyuan.iloc[zeroRowIds, colIds] = 0
sheet_ningxuemeiyuan = sheet_ningxuemeiyuan.iloc[:, colIds:(colIds+1)].groupby(sheet_ningxuemeiyuan['病史ID']).apply(sum, axis=0)
sheet_ningxuemeiyuan.rename(columns={'医嘱剂量' : '凝血酶原复合物_医嘱剂量'}, inplace=True)
sheet_ningxuemeiyuan.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_ningxuemeiyuan, on ='病史ID', how='left')

#Sheet 9
sheet_kangshengsu = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[8].name)
sheet_kangshengsu = Text2Class(sheet_kangshengsu, '药物通用名', useregex=False)
sheet_kangshengsu_norm = sheet_kangshengsu.iloc[:, 0:1].drop_duplicates()

sheet_kangshengsu['实际用量'] = 0
colId = np.where(sheet_kangshengsu.columns == '实际用量')[0][0]
for rowId in range(len(sheet_kangshengsu)):
    if sheet_kangshengsu['使用频次'].iloc[rowId] is np.nan:
        continue
    if sheet_kangshengsu['医嘱结束时间'].iloc[rowId] is np.nan:
        continue

    if sheet_kangshengsu['使用频次'].iloc[rowId] == 'ONCE':
        sheet_kangshengsu.iloc[rowId, colId] = sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]
    elif sheet_kangshengsu['使用频次'].iloc[rowId].find("Q12") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days - 1
        unitNum = 2*wholedays
        if datetime_start.hour >= 9 & datetime_start.hour <21:
            unitNum = unitNum + 1
        elif datetime_start.hour < 9:
            unitNum = unitNum + 2

        if datetime_end.hour >= 9 & datetime_end.hour <21:
            unitNum = unitNum + 1
        elif datetime_end.hour >= 21:
            unitNum = unitNum + 2
        sheet_kangshengsu.iloc[rowId, colId] = unitNum*sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_kangshengsu['使用频次'].iloc[rowId].find("Q8") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum*sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_kangshengsu['使用频次'].iloc[rowId].find("Q6") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum*sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]
    elif sheet_kangshengsu['使用频次'].iloc[rowId].find("Q4") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum*sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_kangshengsu['使用频次'].iloc[rowId].count("-") == 5:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum*sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_kangshengsu['使用频次'].iloc[rowId].count("-") == 3:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum*sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_kangshengsu['使用频次'].iloc[rowId].count("-") == 2:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum*sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_kangshengsu['使用频次'].iloc[rowId].count("-") == 1:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 2 * wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum * sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]
    else:
        datetime_start = datetime.datetime.strptime(sheet_kangshengsu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_kangshengsu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 1 * wholedays
        sheet_kangshengsu.iloc[rowId, colId] = unitNum * sheet_kangshengsu['单次使用剂量(mg)'].iloc[rowId]


colIds= [id for id in range(len(sheet_kangshengsu.columns)) if sheet_kangshengsu.columns[id].find('药物通用名_') >= 0]
for rowId in range(len(sheet_kangshengsu)):
    for eachcolId in colIds:
        if sheet_kangshengsu['药物通用名'].iloc[rowId] is np.nan:
            continue
        if '药物通用名' + "_" + sheet_kangshengsu['药物通用名'].iloc[rowId] == sheet_kangshengsu.columns[eachcolId]:
            sheet_kangshengsu.iloc[rowId, eachcolId] = sheet_kangshengsu['实际用量'].iloc[rowId]

sheet_kangshengsu = sheet_kangshengsu.iloc[:, colIds].groupby(sheet_kangshengsu['病史ID']).apply(sum, axis=0)
sheet_kangshengsu.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_kangshengsu, on ='病史ID', how='left')

sheet_kangshengsu.to_excel(r'D:\Ynby\Doc\Demo/sheet_kangshengsu.xlsx', encoding="UTF-8", na_rep='', index=False)



#Sheet 10
sheet_zhixue = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[9].name)
sheet_zhixue = Text2Class(sheet_zhixue, '其他止血药物')

colname = '氨甲环酸'
colId = np.where(sheet_zhixue.columns == colname)[0][0]
for rowId in range(len(sheet_zhixue)):
    if sheet_zhixue[colname].iloc[rowId] is np.nan:
        continue
    if sheet_zhixue[colname].iloc[rowId] == '否':
        sheet_zhixue.iloc[rowId, colId] = 0
    elif sheet_zhixue[colname].iloc[rowId] == '是':
        sheet_zhixue.iloc[rowId, colId] = 1

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_zhixue, on ='病史ID', how='left')


#Sheet 11
sheet_ningxueyao = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[10].name)
sheet_ningxueyao = Text2Class(sheet_ningxueyao, '药物商品名', useregex=False)

sheet_ningxueyao['实际用量'] = 0
colId = np.where(sheet_ningxueyao.columns == '实际用量')[0][0]
for rowId in range(len(sheet_ningxueyao)):
    if sheet_ningxueyao['使用频次'].iloc[rowId] is np.nan:
        continue
    if sheet_ningxueyao['医嘱结束时间'].iloc[rowId] is np.nan:
        continue

    if sheet_ningxueyao['使用频次'].iloc[rowId] == 'ONCE':
        sheet_ningxueyao.iloc[rowId, colId] = sheet_ningxueyao['单次使用剂量'].iloc[rowId]
    elif sheet_ningxueyao['使用频次'].iloc[rowId].find("Q12") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days - 1
        unitNum = 2*wholedays
        if datetime_start.hour >= 9 & datetime_start.hour <21:
            unitNum = unitNum + 1
        elif datetime_start.hour < 9:
            unitNum = unitNum + 2

        if datetime_end.hour >= 9 & datetime_end.hour <21:
            unitNum = unitNum + 1
        elif datetime_end.hour >= 21:
            unitNum = unitNum + 2
        sheet_ningxueyao.iloc[rowId, colId] = unitNum*sheet_ningxueyao['单次使用剂量'].iloc[rowId]

    elif sheet_ningxueyao['使用频次'].iloc[rowId].find("Q8") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum*sheet_ningxueyao['单次使用剂量'].iloc[rowId]

    elif sheet_ningxueyao['使用频次'].iloc[rowId].find("Q6") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum*sheet_ningxueyao['单次使用剂量'].iloc[rowId]
    elif sheet_ningxueyao['使用频次'].iloc[rowId].find("Q4") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum*sheet_ningxueyao['单次使用剂量'].iloc[rowId]

    elif sheet_ningxueyao['使用频次'].iloc[rowId].count("-") == 5:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum*sheet_ningxueyao['单次使用剂量'].iloc[rowId]

    elif sheet_ningxueyao['使用频次'].iloc[rowId].count("-") == 3:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum*sheet_ningxueyao['单次使用剂量'].iloc[rowId]

    elif sheet_ningxueyao['使用频次'].iloc[rowId].count("-") == 2:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum*sheet_ningxueyao['单次使用剂量'].iloc[rowId]

    elif sheet_ningxueyao['使用频次'].iloc[rowId].count("-") == 1:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 2 * wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum * sheet_ningxueyao['单次使用剂量'].iloc[rowId]
    else:
        datetime_start = datetime.datetime.strptime(sheet_ningxueyao['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_ningxueyao['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 1 * wholedays
        sheet_ningxueyao.iloc[rowId, colId] = unitNum * sheet_ningxueyao['单次使用剂量'].iloc[rowId]



colIds= [id for id in range(len(sheet_ningxueyao.columns)) if sheet_ningxueyao.columns[id].find('药物化学名_') >= 0]
for rowId in range(len(sheet_ningxueyao)):
    for eachcolId in colIds:
        if sheet_ningxueyao['药物化学名'].iloc[rowId] is np.nan:
            continue
        if '药物化学名' + "_" + sheet_ningxueyao['药物化学名'].iloc[rowId] == sheet_ningxueyao.columns[eachcolId]:
            sheet_ningxueyao.iloc[rowId, eachcolId] = sheet_ningxueyao['实际用量'].iloc[rowId]

sheet_ningxueyao = sheet_ningxueyao.iloc[:, colIds].groupby(sheet_ningxueyao['病史ID']).apply(sum, axis=0)
sheet_ningxueyao.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_ningxueyao, on ='病史ID', how='left')

sheet_ningxueyao.to_excel(r'D:\Ynby\Doc\Demo/sheet_ningxueyao.xlsx', encoding="UTF-8", na_rep='', index=False)



#Sheet 12
sheet_xueguanhuoxing = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[11].name)
sheet_xueguanhuoxing = Text2Class(sheet_xueguanhuoxing, '药物商品名', useregex=False)

sheet_xueguanhuoxing['实际用量'] = 0
colId = np.where(sheet_xueguanhuoxing.columns == '实际用量')[0][0]
for rowId in range(len(sheet_xueguanhuoxing)):
    if sheet_xueguanhuoxing['日频次'].iloc[rowId] is np.nan:
        continue
    if sheet_xueguanhuoxing['结束时间'].iloc[rowId] is np.nan:
        continue

    if sheet_xueguanhuoxing['日频次'].iloc[rowId] == 'ONCE':
        sheet_xueguanhuoxing.iloc[rowId, colId] = sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]
    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].find("Q12") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days - 1
        unitNum = 2*wholedays
        if datetime_start.hour >= 9 & datetime_start.hour <21:
            unitNum = unitNum + 1
        elif datetime_start.hour < 9:
            unitNum = unitNum + 2

        if datetime_end.hour >= 9 & datetime_end.hour <21:
            unitNum = unitNum + 1
        elif datetime_end.hour >= 21:
            unitNum = unitNum + 2
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum*sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].find("Q8") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum*sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].find("Q6") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum*sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]
    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].find("Q4") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum*sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].count("-") == 5:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum*sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].count("-") == 3:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum*sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].count("-") == 2:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum*sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_xueguanhuoxing['日频次'].iloc[rowId].count("-") == 1:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 2 * wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum * sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]
    else:
        datetime_start = datetime.datetime.strptime(sheet_xueguanhuoxing['开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_xueguanhuoxing['结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 1 * wholedays
        sheet_xueguanhuoxing.iloc[rowId, colId] = unitNum * sheet_xueguanhuoxing['单次使用剂量(mg)'].iloc[rowId]



colIds= [id for id in range(len(sheet_xueguanhuoxing.columns)) if sheet_xueguanhuoxing.columns[id].find('药物化学名_') >= 0]
for rowId in range(len(sheet_xueguanhuoxing)):
    for eachcolId in colIds:
        if sheet_xueguanhuoxing['药物化学名'].iloc[rowId] is np.nan:
            continue
        if '药物化学名' + "_" + sheet_xueguanhuoxing['药物化学名'].iloc[rowId] == sheet_xueguanhuoxing.columns[eachcolId]:
            sheet_xueguanhuoxing.iloc[rowId, eachcolId] = sheet_xueguanhuoxing['实际用量'].iloc[rowId]

sheet_xueguanhuoxing = sheet_xueguanhuoxing.iloc[:, colIds].groupby(sheet_xueguanhuoxing['病史ID']).apply(sum, axis=0)
sheet_xueguanhuoxing.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_xueguanhuoxing, on ='病史ID', how='left')

sheet_xueguanhuoxing.to_excel(r'D:\Ynby\Doc\Demo/sheet_xueguanhuoxing.xlsx', encoding="UTF-8", na_rep='', index=False)



#Sheet 13
sheet_qitayaowu = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[12].name)
sheet_qitayaowu = Text2Class(sheet_qitayaowu, '药物商品名', useregex=False)

sheet_qitayaowu['实际用量'] = 0
colId = np.where(sheet_qitayaowu.columns == '实际用量')[0][0]
for rowId in range(len(sheet_qitayaowu)):
    if sheet_qitayaowu['使用频次'].iloc[rowId] is np.nan:
        continue
    if sheet_qitayaowu['医嘱结束时间'].iloc[rowId] is np.nan:
        continue

    if sheet_qitayaowu['使用频次'].iloc[rowId] == 'ONCE':
        sheet_qitayaowu.iloc[rowId, colId] = sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]
    elif sheet_qitayaowu['使用频次'].iloc[rowId].find("Q12") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days - 1
        unitNum = 2*wholedays
        if datetime_start.hour >= 9 & datetime_start.hour <21:
            unitNum = unitNum + 1
        elif datetime_start.hour < 9:
            unitNum = unitNum + 2

        if datetime_end.hour >= 9 & datetime_end.hour <21:
            unitNum = unitNum + 1
        elif datetime_end.hour >= 21:
            unitNum = unitNum + 2
        sheet_qitayaowu.iloc[rowId, colId] = unitNum*sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_qitayaowu['使用频次'].iloc[rowId].find("Q8") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum*sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_qitayaowu['使用频次'].iloc[rowId].find("Q6") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum*sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]
    elif sheet_qitayaowu['使用频次'].iloc[rowId].find("Q4") >= 0:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum*sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_qitayaowu['使用频次'].iloc[rowId].count("-") == 5:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 6*wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum*sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_qitayaowu['使用频次'].iloc[rowId].count("-") == 3:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 4*wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum*sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_qitayaowu['使用频次'].iloc[rowId].count("-") == 2:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 3*wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum*sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]

    elif sheet_qitayaowu['使用频次'].iloc[rowId].count("-") == 1:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 2 * wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum * sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]
    else:
        datetime_start = datetime.datetime.strptime(sheet_qitayaowu['医嘱开始时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.datetime.strptime(sheet_qitayaowu['医嘱结束时间'].iloc[rowId], "%Y-%m-%d %H:%M:%S")
        wholedays = (datetime_end.date() - datetime_start.date()).days + 1
        unitNum = 1 * wholedays
        sheet_qitayaowu.iloc[rowId, colId] = unitNum * sheet_qitayaowu['单次使用剂量(mg)'].iloc[rowId]

colIds= [id for id in range(len(sheet_qitayaowu.columns)) if sheet_qitayaowu.columns[id].find('药物化学名_') >= 0]
for rowId in range(len(sheet_qitayaowu)):
    for eachcolId in colIds:
        if sheet_qitayaowu['药物化学名'].iloc[rowId] is np.nan:
            continue
        if '药物化学名' + "_" + sheet_qitayaowu['药物化学名'].iloc[rowId] == sheet_qitayaowu.columns[eachcolId]:
            sheet_qitayaowu.iloc[rowId, eachcolId] = sheet_qitayaowu['实际用量'].iloc[rowId]

sheet_qitayaowu = sheet_qitayaowu.iloc[:, colIds].groupby(sheet_qitayaowu['病史ID']).apply(sum, axis=0)
sheet_qitayaowu.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_qitayaowu, on ='病史ID', how='left')

sheet_qitayaowu.to_excel(r'D:\Ynby\Doc\Demo/sheet_qitayaowu.xlsx', encoding="UTF-8", na_rep='', index=False)


#Sheet 14
sheet_tiwenjilu = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[13].name)
colIds = [4, 5, 6, 7, 9, 10, 11]
sheet_tiwenjilu = sheet_tiwenjilu.iloc[:, colIds].groupby(sheet_tiwenjilu['病史ID']).apply(np.mean, axis=0)
sheet_tiwenjilu.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_tiwenjilu, on ='病史ID', how='left')

#Sheet 15
sheet_xuetangjilu = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[14].name)
colId = 2
sheet_xuetangjilu = sheet_xuetangjilu.iloc[:, colId:(colId+1)].groupby(sheet_xuetangjilu['病史ID']).apply(np.mean, axis=0)
sheet_xuetangjilu.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_xuetangjilu, on ='病史ID', how='left')


#Sheet 16
sheet_bingfazheng = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[15].name)

for colId in range(1, len(sheet_bingfazheng.columns)):
    for rowId in range(len(sheet_bingfazheng)):
        if sheet_bingfazheng.iloc[rowId, colId] is np.nan:
            continue
        if sheet_bingfazheng.iloc[rowId, colId] == '否':
            sheet_bingfazheng.iloc[rowId, colId] = 0
        else:
            sheet_bingfazheng.iloc[rowId, colId] = 1

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_bingfazheng, on ='病史ID', how='left')


#Sheet 17
sheet_diedao = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[16].name)
for colId in range(1, len(sheet_diedao.columns)):
    for rowId in range(len(sheet_diedao)):
        if sheet_diedao.iloc[rowId, colId] is np.nan:
            continue
        if sheet_diedao.iloc[rowId, colId] == '否':
            sheet_diedao.iloc[rowId, colId] = 0
        else:
            sheet_diedao.iloc[rowId, colId] = 1

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_diedao, on ='病史ID', how='left')


#Sheet 18
sheet_daoniao = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[17].name)
for colId in range(1, len(sheet_daoniao.columns)):
    for rowId in range(len(sheet_daoniao)):
        if sheet_daoniao.iloc[rowId, colId] is np.nan:
            continue
        if sheet_daoniao.iloc[rowId, colId] == '否':
            sheet_daoniao.iloc[rowId, colId] = 0
        else:
            sheet_daoniao.iloc[rowId, colId] = 1

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_daoniao, on ='病史ID', how='left')


#Sheet 19
sheet_zhenduanzhuangui = pd.read_excel(os.path.join(parent_folder, filename), sheetname='诊断及转规')
colId = np.where(sheet_zhenduanzhuangui.columns == '出院转归')[0][0]

for rowId in range(len(sheet_zhenduanzhuangui)):
    if sheet_zhenduanzhuangui.iloc[rowId, colId] is np.nan:
        continue
    if sheet_zhenduanzhuangui.iloc[rowId, colId].find('医嘱') == 0:
        sheet_zhenduanzhuangui.iloc[rowId, colId] = 0
    elif (sheet_zhenduanzhuangui.iloc[rowId, colId] == '死亡') | (sheet_zhenduanzhuangui.iloc[rowId, colId] == '非医嘱离院'):
        sheet_zhenduanzhuangui.iloc[rowId, colId] = 1
    elif sheet_zhenduanzhuangui.iloc[rowId, colId] == '-':
        sheet_zhenduanzhuangui.iloc[rowId, colId] = np.nan

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_zhenduanzhuangui, on ='病史ID', how='left')

#Sheet 20
sheet_xinzangzhibiao = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[19].name)
colIds = [1, 2, 3, 4]
sheet_xinzangzhibiao = sheet_xinzangzhibiao.iloc[:, colIds].groupby(sheet_xinzangzhibiao['病史ID']).apply(np.mean, axis=0)
sheet_xinzangzhibiao.reset_index(drop=False, inplace=True)

allMergedBleedShockDf = pd.merge(allMergedBleedShockDf, sheet_xinzangzhibiao, on ='病史ID', how='left')

allMergedBleedShockDf.drop(['既往合并症', '其他止血药物', '尿量', '伤口引流量(ml)', '血糖(mmol/L)_y'], axis=1, inplace=True)
# allMergedBleedShockDf.drop(['入ICU前/基线-1（1/0）', '入ICU第1天（即刻）-1（1/0）', '入ICU第2天-1（1/0）', '入ICU第3天-1（1/0）', '入ICU第4天-1（1/0）',  \
#                             '入ICU第5天-1（1/0）', '入ICU第6天-1（1/0）', '入ICU第7天-1（1/0）', '入ICU第14天-1（1/0）', '出院前-1（1/0）'], axis=1, inplace=True)

for eachprefix in ['手术名称_', '麻醉方式_', '手术级别_', '手术总次数', '手术时长(时)', '手术输血-血浆(ml)', '输浓缩红细胞量(u)', '输血浆量(ml)']:
    colIds = [id for id in range(len(allMergedBleedShockDf.columns)) if allMergedBleedShockDf.columns[id].find(eachprefix) >= 0]
    for eachcolId in colIds:
        allMergedBleedShockDf.iloc[np.where(np.isnan(allMergedBleedShockDf.iloc[:, eachcolId]))[0], eachcolId] = 0

allMergedBleedShockDf.to_csv(r'D:\Ynby\Doc\Demo/出血性休克院前+院后数据_清洗干净_分类.csv', encoding="UTF-8", na_rep='', index=False)
allMergedBleedShockDf.to_excel(r'D:\Ynby\Doc\Demo/出血性休克院前+院后数据_清洗干净_分类.xlsx', encoding="UTF-8", na_rep='', index=False)

allMergedBleedShockDf_outcome = allMergedBleedShockDf.iloc[[rowId for rowId in range(len((allMergedBleedShockDf))) if allMergedBleedShockDf['出院转归'].iloc[rowId] is not np.nan], :]
allMergedBleedShockDf_outcome['出院转归'].astype(np.int)
allMergedBleedShockDf_outcome.to_csv(r'D:\Ynby\Doc\Demo/出血性休克院前+院后数据_清洗干净_二分类.csv', encoding="UTF-8", na_rep='', index=False)
allMergedBleedShockDf_outcome.to_excel(r'D:\Ynby\Doc\Demo/出血性休克院前+院后数据_清洗干净_二分类.xlsx', encoding="UTF-8", na_rep='', index=False)


allMergedBleedShockDf_recovery = allMergedBleedShockDf_outcome[allMergedBleedShockDf_outcome['出院转归'] == 0]
allMergedBleedShockDf_recovery.to_csv(r'D:\Ynby\Doc\Demo/出血性休克院前+院后数据_清洗干净_医嘱离转院住院时间.csv', encoding="UTF-8", na_rep="", index=False)
allMergedBleedShockDf_recovery.to_excel(r'D:\Ynby\Doc\Demo/出血性休克院前+院后数据_清洗干净_医嘱离转院住院时间.xlsx', encoding="UTF-8", na_rep="", index=False)


