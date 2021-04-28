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
import baidu_nlp as baidunlp


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
# 1.患者基本信息.xlsx 就诊年龄, 性别
# 3、EMR.病史(含查体).xlsx ： 现病史, 既往史, 家族史（遗传病）, 查体（包括血压等）
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


bicong_parent_folder = r'D:\Ynby\Doc\Demo\臂丛/'
bicong_BingShiData = pd.read_excel(bicong_parent_folder + '臂丛数据.xlsx', encoding="UTF-8", na_rep="", index=True)

b = baidunlp.baidu_nlp_ts()

historyColnames = ['主诉', '现病史', '既往史', '家族史', '查体']
for historyColname in historyColnames:
    sentence_list = []
    for rowId in range(len(bicong_BingShiData)):
        time.sleep(1)
        if bicong_BingShiData[historyColname].iloc[rowId] is np.nan:
            continue

        res = b.lexer(bicong_BingShiData[historyColname].iloc[rowId])
        lexerDf = pd.DataFrame(res['items'])

        # seg_list = jieba.cut_for_search(bicong_BingShiData['现病史'].iloc[rowId])  # 搜索引擎模式
        eachSentence = []
        lastStr = ''
        new_seg_list = []
        for eachstr in lexerDf['item']:
            new_seg_list = new_seg_list + [eachstr]

        for id in range(len(new_seg_list[::-1])):
            eachstr = new_seg_list[::-1][id]
            if id == len(new_seg_list[::-1]) -1:
                if len(eachSentence) > 0:
                    sentence_list = sentence_list + [eachSentence]
            elif eachstr in sepcharacter:
                if len(eachSentence) > 0:
                    sentence_list = sentence_list+ [eachSentence]
                eachSentence = []
                lastStr = ''
            else:
                if is_number(eachstr):
                    if len(eachSentence) > 0:
                        sentence_list = sentence_list + [eachSentence]
                    eachSentence = []
                    lastStr = ''
                    continue
                if lastStr.find(eachstr) >=0:
                    continue
                eachSentence = eachSentence + [eachstr]
                lastStr = eachstr

    sentence_list = sentence_list[::-1]
    new_sentence_list = []
    for eachSentence in sentence_list:
        new_sentence_list = new_sentence_list + [eachSentence[::-1]]

    all_sentence_list = []
    for eachSentence in new_sentence_list:
        newSentence = eachSentence
        for id1 in range(len(eachSentence)-1):
            for id2 in range(id1+2, len(eachSentence)+1):
                newSentence = newSentence + ["".join(eachSentence[id1:id2])]
        all_sentence_list = all_sentence_list + [newSentence]

    allinone_list = []
    for eachSentence in all_sentence_list:
        allinone_list = allinone_list + eachSentence

    counter = Counter(allinone_list)
    dictionary=dict(counter)
    # get to k most frequently occuring words
    k=10000
    res=counter.most_common(k)

    WordFreqDf = pd.DataFrame(res)
    WordFreqDf.columns = ['关键词', '计数']
    WordFreqDf.to_csv(r'D:\Ynby\Doc\Demo/臂丛/臂丛Flat'+ historyColname + '词频_baidu.csv', encoding="UTF-8", na_rep="", index=False)
    WordFreqDf.to_excel(r'D:\Ynby\Doc\Demo/臂丛/臂丛Flat'+ historyColname + '词频_baidu.xlsx', encoding="UTF-8", na_rep="", index=False)









