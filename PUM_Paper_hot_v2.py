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

# https://blog.csdn.net/weixin_37773766/article/details/80925645

zhfont1 = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=20)

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# https://chenzhen.blog.csdn.net/article/details/103378351?utm_term=z%E6%A3%80%E9%AA%8C&utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~sobaiduweb~default-1-103378351&spm=3001.4430

parent_folder = r'D:\Ynby\Doc\协和Demo'

allwebofscienceMap = pd.read_excel(r'D:\Ynby\Doc\协和Demo/webofscience字段映射.xlsx', encoding='UTF-8')
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
    fullcolnames = allwebofscienceMap['缩写'].values.tolist()
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
            endFlag = False
            WaitFirstLine = True
            for eachrowId in range(articleStartRowIds[rowId]+1, endRowId-1):
                if linesSeries.iloc[eachrowId].startswith(colnames[colId]):
                    articlesDf.iloc[rowId, colId] = linesSeries.iloc[eachrowId][(len(colnames[colId])+1):]
                    WaitFirstLine = False
                else:
                    endFlag = False
                    for othercolId in range(len(fullcolnames)):
                        if othercolId == colId:
                            continue
                        elif (WaitFirstLine == False) & (linesSeries.iloc[eachrowId].startswith(fullcolnames[othercolId])):
                            endFlag=True
                            break

                    if endFlag == True:
                        break
                    else:
                        if WaitFirstLine == False:
                            articlesDf.iloc[rowId, colId] = articlesDf.iloc[rowId, colId] + "; " + linesSeries.iloc[eachrowId][(len(colnames[colId]) + 1):]

    articlesDf.to_excel(parent_folder + r'/' + eachPaperfile + r'_articlesDf.xlsx', encoding="UTF-8", na_rep="", index=True)

#作者关键字
    articlesDE = articlesDf['DE']
    articlesDE.dropna(inplace=True)
    allkeywords = []
    for rowId in range(len(articlesDE)):
        eachkeywords = articlesDE.iloc[rowId].split("; ")
        allkeywords = allkeywords + [eachkey.replace(", ", ".").replace(" ", ".") for eachkey in eachkeywords]

    wl_space_split = " ".join([eachstr for eachstr in allkeywords])

    allkeywordsDf = pd.DataFrame(allkeywords)
    allkeywordsCount = allkeywordsDf[0].value_counts()
    allkeywordsCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_DE关键字词频.xlsx', encoding="UTF-8", na_rep="", index=True)

    my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None).generate_from_frequencies(allkeywordsCount)

    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.show()

    my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_DE关键字wordcloud.png')


#检索关键字
    articlesID = articlesDf['ID']
    articlesID.dropna(inplace=True)
    if len(articlesID) > 0:
        allkeywords = []
        for rowId in range(len(articlesID)):
            eachkeywords = articlesID.iloc[rowId].split("; ")
            allkeywords = allkeywords + [eachkey.replace(", ", ".").replace(" ", ".") for eachkey in eachkeywords]

        wl_space_split = " ".join([eachstr for eachstr in allkeywords])

        allkeywordsDf = pd.DataFrame(allkeywords)
        allkeywordsCount = allkeywordsDf[0].value_counts()
        allkeywordsCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_ID词频.xlsx', encoding="UTF-8", na_rep="", index=True)

        my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None).generate_from_frequencies(allkeywordsCount)

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_ID_wordcloud.png')



#期刊名称
    articlesSO = articlesDf['SO']
    articlesSO.dropna(inplace=True)
    if len(articlesSO) > 0:
        allkeywords = []
        for rowId in range(len(articlesSO)):
            eachkeywords = articlesSO.iloc[rowId].split("; ")
            allkeywords = allkeywords + [eachkey.replace(", ", ".").replace(" ", ".") for eachkey in eachkeywords]

        wl_space_split = " ".join([eachstr for eachstr in allkeywords])

        allkeywordsDf = pd.DataFrame(allkeywords)
        allkeywordsCount = allkeywordsDf[0].value_counts()
        allkeywordsCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_SO期刊名词频.xlsx', encoding="UTF-8", na_rep="",
                                  index=True)

        my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None, collocations=False).generate_from_frequencies(allkeywordsCount)

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_SO期刊名_wordcloud.png')


#作者
    articlesAU = articlesDf['AU']
    articlesAU.dropna(inplace=True)

    allkeywords = []
    for rowId in range(len(articlesAU)):
        eachkeywords = articlesAU.iloc[rowId].split("; ")
        allkeywords = allkeywords + [eachkey.replace(", ", ".").replace(" ", ".") for eachkey in eachkeywords]

    wl_space_split = " ".join([eachstr for eachstr in allkeywords])

    allkeywordsDf = pd.DataFrame(allkeywords)
    allkeywordsCount = allkeywordsDf[0].value_counts()
    allkeywordsCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_AU作者词频.xlsx', encoding="UTF-8", na_rep="", index=True)

    my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None, collocations=False).generate_from_frequencies (allkeywordsCount)

    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.show()

    my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_AU作者_wordcloud.png')



#被引
    articlesCR = articlesDf['CR']
    articlesCR.dropna(inplace=True)
    if len(articlesCR) > 0:
        allRefDf = []
        for rowId in range(len(articlesCR)):
            eachkeywords = articlesCR.iloc[rowId].split("; ")
            eachRefDf = []
            for eachRowId in range(len(eachkeywords)):
                # singleRef = eachkeywords[eachRowId].split(", ")
                singleRef = eachkeywords[eachRowId]
                matchedYears = re.findall(' \d{4},', singleRef)
                if len(matchedYears) == 0:
                    continue
                matchedYears = [eachstr.replace(" ", "").replace(",", "") for eachstr in matchedYears]
                if len(matchedYears) > 0:
                    if (int(matchedYears[0]) >= 1900) & (int(matchedYears[0]) < 2100):
                        yearVal = int(matchedYears[0])
                        startYearIndex = singleRef.index(str(yearVal))
                        AuthorStr = singleRef[:startYearIndex].split(", ")[0].replace(", ", ".").replace(" ", ".")
                        OtherStr = singleRef[(startYearIndex+6):]
                        OtherStrs = OtherStr.split(", ")
                        OtherRef = [eachkey.strip().replace(", ", ".").replace(" ", ".") for eachkey in OtherStrs]
                        if len(OtherRef) != 4:
                            continue
                        singleRef = [AuthorStr] + [yearVal] + OtherRef
                    else:
                        continue
                else:
                    continue

                # singleRef = [eachkey.strip().replace(", ", ".").replace(" ", ".") for eachkey in singleRef]
                if len(eachRefDf) == 0:
                    eachRefDf = pd.DataFrame(singleRef).transpose()
                else:
                    eachRefDf = pd.concat([eachRefDf, pd.DataFrame(singleRef).transpose()], axis=0)

            if len(eachRefDf) == 0:
                continue
            if len(allRefDf) == 0:
                allRefDf = eachRefDf
            else:
                allRefDf = pd.concat([allRefDf, eachRefDf], axis=0)


        # allRefDf = allRefDf.iloc[:, 0:3]
        allRefDf = allRefDf.iloc[:, [0,1,2]+[5]]
        allRefDf.columns = ['Author', 'Year', 'JournalName', 'Title']

#CR被引作者
        allRefAuthorCount = allRefDf['Author'].value_counts()
        allRefAuthorCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_CR被引作者词频.xlsx', encoding="UTF-8", na_rep="", index=True)

        my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None, collocations=False).generate_from_frequencies(allRefAuthorCount)

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_CR被引作者_wordcloud.png')


#CR被引文章
        allRefTitleCount = allRefDf['Title'].value_counts()
        allRefTitleCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_CR被引文章词频.xlsx', encoding="UTF-8", na_rep="", index=True)

        my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None, collocations=False).generate_from_frequencies(allRefTitleCount)

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_CR被引文章_wordcloud.png')



#CR被引年份
        allRefYearCount = allRefDf['Year'].value_counts()
        allRefYearCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_CR被引年份词频.xlsx', encoding="UTF-8", na_rep="", index=True)

        allRefYearCount.index = allRefYearCount.index.astype("str")
        my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None, collocations=False).generate_from_frequencies(allRefYearCount)

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_CR被引年份_wordcloud.png')


#CR被引刊物
        allRefJournalCount = allRefDf['JournalName'].value_counts()
        allRefJournalCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_CR被引刊物词频.xlsx', encoding="UTF-8", na_rep="", index=True)

        my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None, collocations=False).generate_from_frequencies(allRefJournalCount)

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_CR被引刊物_wordcloud.png')


#CR年度论文数量
        allRefYearTitle = allRefDf.iloc[:, [1,3]]
        allRefYearTitle['Year'] = allRefYearTitle['Year'].astype(int)
        allRefYearTitle.dropna(inplace=True)
        allRefYearTitle.drop_duplicates(inplace=True)
        allRefYearTitle = allRefYearTitle['Year'].value_counts()

        allRefYearCount.to_excel(parent_folder + r'/' + eachPaperfile + r'_CR被引论文数量按年份词频.xlsx', encoding="UTF-8", na_rep="", index=True)

        my_wordcloud = WordCloud(width=800, height=600, mode='RGBA', background_color=None, collocations=False).generate_from_frequencies(allRefYearCount)

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        my_wordcloud.to_file(parent_folder + r'/images/' + eachPaperfile + '_CR被引论文数量按年份_wordcloud.png')


        allRefYearTitle= pd.DataFrame(allRefYearTitle)
        allRefYearTitle.reset_index(inplace=True)
        allRefYearTitle.sort_values(by='index',inplace=True)

        allRefYearTitle = allRefYearTitle[allRefYearTitle['index'] > 1980]

        fig, ax = plt.subplots()
        ax.xaxis.grid(True, which='major', linewidth=2)
        plt.plot(allRefYearTitle['index'].values, allRefYearTitle['Year'].values,'-*')
        plt.title(u'历史论文发表数量', fontproperties=zhfont1)
        plt.xlabel('年份', fontproperties=zhfont1)
        plt.ylabel('论文数量', fontproperties=zhfont1)
        plt.legend(prop=zhfont1)
        # plt.xticks([0, 5, 5+12, 5+24, 5+36, 5+48, 5+54],('201408', '201501', '201601', '201701', '201801', '201901', '201907'), rotation=70)
        plt.savefig(parent_folder + r'/images/' + eachPaperfile + '_CR历史论文发表数量.jpg')
        plt.show()



