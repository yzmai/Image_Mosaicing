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

# https://blog.csdn.net/Bill_zhang5/article/details/80228441

zhfont1 = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=40)
zhfontsmall = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=12)
zhfontmiddle = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=25)
zhfontlabel = font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf',size=18)


if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# https://chenzhen.blog.csdn.net/article/details/103378351?utm_term=z%E6%A3%80%E9%AA%8C&utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~sobaiduweb~default-1-103378351&spm=3001.4430

parent_folder = r'D:\Ynby\Doc\协和Demo'

GSSNicData = pd.read_excel(parent_folder + r'/GSS数据 Nic_已清洗.xlsx', encoding='UTF-8')


fenxingCol = GSSNicData['OLF分型'].values
colId = np.where(GSSNicData.columns == 'OLF分型')[0][0]
for rowId in range(len(GSSNicData)):
    if fenxingCol[rowId] == '跳跃':
        GSSNicData.iloc[rowId, colId] = 2
    elif fenxingCol[rowId] == '连续':
        GSSNicData.iloc[rowId, colId] = 1
    elif fenxingCol[rowId] == '孤立':
        GSSNicData.iloc[rowId, colId] = 0

fenxingCol = GSSNicData['OPLL分型'].values
colId = np.where(GSSNicData.columns == 'OPLL分型')[0][0]
for rowId in range(len(GSSNicData)):
    if fenxingCol[rowId] == '混合':
        GSSNicData.iloc[rowId, colId] = 3
    elif fenxingCol[rowId] == '节段':
        GSSNicData.iloc[rowId, colId] = 2
    elif fenxingCol[rowId] == '连续':
        GSSNicData.iloc[rowId, colId] = 1
    elif fenxingCol[rowId] == '孤立':
        GSSNicData.iloc[rowId, colId] = 0



dishCol = GSSNicData['DISH'].values
colId = np.where(GSSNicData.columns == 'DISH')[0][0]
for rowId in range(len(GSSNicData)):
    if dishCol[rowId] == '+':
        GSSNicData.iloc[rowId, colId] = 1
    elif dishCol[rowId] == '-':
        GSSNicData.iloc[rowId, colId] = 0


dishCol = GSSNicData['二便障碍'].values
colId = np.where(GSSNicData.columns == '二便障碍')[0][0]
for rowId in range(len(GSSNicData)):
    if dishCol[rowId] == '+':
        GSSNicData.iloc[rowId, colId] = 1
    elif dishCol[rowId] == '-':
        GSSNicData.iloc[rowId, colId] = 0

dishCol = GSSNicData['双下肢不全瘫'].values
colId = np.where(GSSNicData.columns == '双下肢不全瘫')[0][0]
for rowId in range(len(GSSNicData)):
    if dishCol[rowId] == '+':
        GSSNicData.iloc[rowId, colId] = 1
    elif dishCol[rowId] == '-':
        GSSNicData.iloc[rowId, colId] = 0


# GSSNicData = GSSNicData.iloc[:, 0:(len(GSSNicData)-3)]

CorrelationMatrix = GSSNicData.corr()

fig = plt.figure()
ax = fig.add_subplot(111)
cax = ax.matshow(CorrelationMatrix, vmin=0.1, vmax=1)
fig.colorbar(cax)
ticks = np.arange(0,len(CorrelationMatrix),1)
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.set_xticklabels(CorrelationMatrix.columns.values.tolist(), fontproperties=zhfontsmall, rotation=90)
ax.set_yticklabels(CorrelationMatrix.columns.values.tolist(), fontproperties=zhfontsmall)
plt.savefig(parent_folder + r'/协和GSS_Nic_相关矩阵.jpg')
plt.show()

CorrelationMatrix.to_excel(parent_folder+r'/协和GSS_Nic_相关矩阵.xlsx', encoding="UTF-8", na_rep="", index=True)
