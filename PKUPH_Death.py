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


def loadDataSet():
    filename = r'D:\Ynby\Doc\Demo/北京大学人民医院_王储0323需求1-死亡患者FINAL_已清洗.xlsx'
    b = xlrd.open_workbook(filename)
    sheet_yuanqian = pd.read_excel(os.path.join(parent_folder, filename), sheetname=b.sheets()[0].name)

    blacklistwords = ['呼吸', 'I型', 'II型', '重症', '分', 'L', '极高危', '双侧']
    sheet_yuanyin = Text2Class(sheet_yuanqian, '死亡原因')
    colIds = [id for id in range(len(sheet_yuanyin.columns)) if sheet_yuanyin.columns.values[id].find('死亡原因_') == 0]
    allData = []
    for rowId in range(len(sheet_yuanyin)):
        eachRowData = []
        for colId in colIds:
            if sheet_yuanyin.iloc[rowId, colId] >0:
                eachReason = sheet_yuanyin.columns.values[colId].replace("死亡原因_", "")
                if eachReason not in blacklistwords:
                    eachRowData = eachRowData + [eachReason]
        if eachRowData != []:
            allData = allData + [eachRowData]

    return allData


def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
    C1.sort()
    # 映射为frozenset唯一性的，可使用其构造字典
    return list(map(frozenset, C1))


# 从候选K项集到频繁K项集（支持度计算）
def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                if not can in ssCnt:
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1
    numItems = float(len(D))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key] / numItems
        if support >= minSupport:
            retList.insert(0, key)
            supportData[key] = support
    return retList, supportData


def calSupport(D, Ck, min_support):
    dict_sup = {}
    for i in D:
        for j in Ck:
            if j.issubset(i):
                if not j in dict_sup:
                    dict_sup[j] = 1
                else:
                    dict_sup[j] += 1
    sumCount = float(len(D))
    supportData = {}
    relist = []
    for i in dict_sup:
        temp_sup = dict_sup[i] / sumCount
        if temp_sup >= min_support:
            relist.append(i)
            supportData[i] = temp_sup  # 此处可设置返回全部的支持度数据（或者频繁项集的支持度数据）
    return relist, supportData


# 改进剪枝算法
def aprioriGen(Lk, k):  # 创建候选K项集 ##LK为频繁K项集
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i + 1, lenLk):
            L1 = list(Lk[i])[:k - 2]
            L2 = list(Lk[j])[:k - 2]
            L1.sort()
            L2.sort()
            if L1 == L2:  # 前k-1项相等，则可相乘，这样可防止重复项出现
                #  进行剪枝（a1为k项集中的一个元素，b为它的所有k-1项子集）
                a = Lk[i] | Lk[j]  # a为frozenset()集合
                a1 = list(a)
                b = []
                # 遍历取出每一个元素，转换为set，依次从a1中剔除该元素，并加入到b中
                for q in range(len(a1)):
                    t = [a1[q]]
                    tt = frozenset(set(a1) - set(t))
                    b.append(tt)
                t = 0
                for w in b:
                    # 当b（即所有k-1项子集）都是Lk（频繁的）的子集，则保留，否则删除。
                    if w in Lk:
                        t += 1
                if t == len(b):
                    retList.append(b[0] | b[1])
    return retList


def apriori(dataSet, minSupport=0.2):
    C1 = createC1(dataSet)
    D = list(map(set, dataSet))  # 使用list()转换为列表
    L1, supportData = calSupport(D, C1, minSupport)
    L = [L1]  # 加列表框，使得1项集为一个单独元素
    k = 2
    while (len(L[k - 2]) > 0):
        Ck = aprioriGen(L[k - 2], k)
        Lk, supK = scanD(D, Ck, minSupport)  # scan DB to get Lk
        supportData.update(supK)
        L.append(Lk)  # L最后一个值为空集
        k += 1
    del L[-1]  # 删除最后一个空集
    return L, supportData  # L为频繁项集，为一个列表，1，2，3项集分别为一个元素。


# 生成集合的所有子集
def getSubset(fromList, toList):
    for i in range(len(fromList)):
        t = [fromList[i]]
        tt = frozenset(set(fromList) - set(t))
        if not tt in toList:
            toList.append(tt)
            tt = list(tt)
            if len(tt) > 1:
                getSubset(tt, toList)


def calcConf(freqSet, H, supportData, ruleList, minConf=0.7):
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet - conseq]  # 计算置信度
        # 提升度lift计算lift = p(a & b) / p(a)*p(b)
        lift = supportData[freqSet] / (supportData[conseq] * supportData[freqSet - conseq])

        if conf >= minConf and lift > 1:
            print(freqSet - conseq, '-->', conseq, '支持度', round(supportData[freqSet - conseq], 2), '置信度：', conf,
                  'lift值为：', round(lift, 2))
            ruleList.append((freqSet - conseq, conseq, conf))


# 生成规则
def gen_rule(L, supportData, minConf=0.7):
    bigRuleList = []
    for i in range(1, len(L)):  # 从二项集开始计算
        for freqSet in L[i]:  # freqSet为所有的k项集
            # 求该三项集的所有非空子集，1项集，2项集，直到k-1项集，用H1表示，为list类型,里面为frozenset类型，
            H1 = list(freqSet)
            all_subset = []
            getSubset(H1, all_subset)  # 生成所有的子集
            calcConf(freqSet, all_subset, supportData, bigRuleList, minConf)
    return bigRuleList



#生成关联规则
# 创建关联规则
def generateRules(fileName, L, supportData, minConf=0.7):  # supportData是从scanD获得的字段
    bigRuleList = []
    for i in range(1, len(L)):  # 只获得又有2个或以上的项目的集合
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            if (i > 1):
                rulesFromConseq(fileName, freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(fileName, freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList

# 实例数、支持度、置信度和提升度评估
def calcConf(fileName, freqSet, H, supportData, brl, minConf=0.7):
    prunedH = []
    D = fileName
    numItems = float(len(D))
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet - conseq]  # 计算置信度
        if conf >= minConf:
            instances = numItems * supportData[freqSet]  # 计算实例数
            liftvalue = conf / supportData[conseq]  # 计算提升度
            brl.append((freqSet - conseq, conseq, int(instances), round(supportData[freqSet], 4), round(conf, 4),
                        round(liftvalue, 4)))  # 支持度已经在SCAND中计算得出
            prunedH.append(conseq)
    return prunedH

# 生成候选规则集
def rulesFromConseq(fileName, freqSet, H, supportData, brl, minConf=0.7):
    m = len(H[0])
    if (len(freqSet) > (m + 1)):
        Hmp1 = aprioriGen(H, m + 1)
        Hmp1 = calcConf(fileName, freqSet, Hmp1, supportData, brl, minConf)
        if (len(Hmp1) > 1):
            rulesFromConseq(fileName, freqSet, Hmp1, supportData, brl, minConf)

if __name__ == '__main__':

    dataSet = loadDataSet()
    L, supportData = apriori(dataSet, minSupport=0.002)
    # rule = gen_rule(L, supportData, minConf=0.5)
    rules = generateRules(dataSet, L, supportData, minConf=0.5)

    df = pd.DataFrame(rules,  columns=['item1',  'item2',  'instance',  'support', 'confidence', 'lift'])  # 创建频繁规则数据框
    df_lift = df[df['lift'] > 1.0]  # 只选择提升度>1的规则
    df_lift['item1'] = [list(eachVal) for eachVal in df_lift['item1'].values]
    df_lift['item2'] = [list(eachVal) for eachVal in df_lift['item2'].values]
    for rowId in range(len(df_lift)):
        df_lift.iloc[rowId, 0] = ','.join(df_lift.iloc[rowId, 0])
    goodRowIds = []
    for rowId in range(len(df_lift)):
        found = False
        for eachId in df_lift.iloc[rowId, 1]:
            if df_lift.iloc[rowId, 0].find(eachId) >= 0:
                found = True
                break
        if found == False:
            goodRowIds = goodRowIds + [rowId]
        df_lift.iloc[rowId, 1] = ','.join(df_lift.iloc[rowId, 1])
    df_lift = df_lift.iloc[goodRowIds, :]

    goodRowIds = []
    for rowId in range(len(df_lift)):
        if df_lift.iloc[rowId, 0].find(df_lift.iloc[rowId, 1]) < 0:
            goodRowIds = goodRowIds + [rowId]
    df_lift = df_lift.iloc[goodRowIds, :]

    df_lift.rename(columns={'item1':'先验', 'item2':'后验', 'instance':'样本数量', 'support':'支持度', 'confidence':'置信度', 'lift':'提升度'}, inplace=True)  # 创建频繁规则数据框
    df_lift.sort_values('置信度', ascending=False, inplace=True)
    df_lift.to_csv(r'D:\Ynby\Doc\Demo/死亡原因_关联规则.csv', encoding="UTF-8", na_rep="", index=False)
    df_lift.to_excel(r'D:\Ynby\Doc\Demo/死亡原因_关联规则.xlsx', encoding="UTF-8", na_rep="", index=False)


