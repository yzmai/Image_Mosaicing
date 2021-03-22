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
from wordcloud import WordCloud

# https://blog.csdn.net/OrdinaryMatthew/article/details/107064400
# AU：作者 （Author Full Name）
# TI：文章标题（Document Title）
# SO：期刊名（Publication Name）
# VL：卷号（Volume）
# IS：期号（Issue）
# BP: 起始页码（Beginning Page）
# EP： 终止页码（Ending Page）
# DI： DOI（Digital Object Identifier）
# PD： 出版日期（Publication Date）
# PY： 出版年（Year Published）
# AF：作者全名（Author Full Name）
# OI：ORCID Identifier （Open Researcher and Contributor ID）
# SN：ISSN
# EI ： 电子期刊的ISSN（eISSN）
# UT： 入藏号（Accession Number）

zhfont1 = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=20)

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# https://chenzhen.blog.csdn.net/article/details/103378351?utm_term=z%E6%A3%80%E9%AA%8C&utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~sobaiduweb~default-1-103378351&spm=3001.4430

parent_folder = r'D:\Ynby\Doc\协和Demo'
hospital_in_list = os.listdir(parent_folder)
# calendarData = calendar.get_all_calendar()

webofscienceMap = pd.read_excel(r'D:\Ynby\Doc\协和Demo/webofscience字段映射_concerned.xlsx', encoding='UTF-8')
paperfiles = [r'(endochondral ossification) AND (scaffold)', r'(endochondral ossification) AND (tissue engineering)']

for eachPaperfile in paperfiles:
    paperData = open(parent_folder + '/' + eachPaperfile + '_utf8.txt', encoding='UTF-8')
    lines = paperData.readlines()

    linesSeries =  pd.Series(lines)
    for rowId in range(len(linesSeries)):
        linesSeries.iloc[rowId] = linesSeries.iloc[rowId].replace("\n", "")

    articleStartRowIds = np.where(linesSeries == 'PT J')[0]

    articlesDf = pd.DataFrame(np.zeros((len(articleStartRowIds), webofscienceMap.shape[0])))
    colnames = webofscienceMap['缩写'].values.tolist()
    articlesDf.columns = colnames
    for rowId in range(len(articlesDf)):
            for colId in range(articlesDf.shape[1]):
                articlesDf.iloc[rowId, colId] = np.nan

    for rowId in range(len(articleStartRowIds)):
        if rowId == len(articleStartRowIds)-1:
            endRowId = len(articleStartRowIds)
        else:
            endRowId = articleStartRowIds[rowId+1]
        for colId in range(len(colnames)):
            found = False
            for eachrowId in range(articleStartRowIds[rowId]+1, endRowId-1):
                if linesSeries.iloc[eachrowId].startswith(colnames[colId]):
                    articlesDf.iloc[rowId, colId] = linesSeries.iloc[eachrowId][(len(colnames[colId])+1):]
                # else:
                #     endFlag = False
                #     for othercolId in range(len(colnames)):
                #         if othercolId == colId:
                #             continue
                #         elif linesSeries.iloc[eachrowId].startswith(colnames[othercolId]):
                #             endFlag=True
                #             break
                #
                #     if endFlag == True:
                #         break
                #     else:
                #         articlesDf.iloc[rowId, colId] = linesSeries.iloc[eachrowId][(len(colnames[colId]) + 1):]



    articlesDE = articlesDf['DE']
    articlesDE.dropna(inplace=True)
    wl_space_split = " ".join([eachstr for eachstr in articlesDE.values.tolist()])

    allkeywords = []
    for rowId in range(len(articlesDE)):
        eachkeywords = articlesDE.iloc[rowId].split("; ")
        allkeywords = allkeywords + eachkeywords

    allkeywordsDf = pd.DataFrame(allkeywords)
    allkeywordsCount = allkeywordsDf[0].value_counts()
    allkeywordsCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_关键字词频.xlsx', encoding="UTF-8", na_rep="", index=True)

    my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None).generate(wl_space_split)

    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.show()

    my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_wordcloud.png')











