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


AKI_Df=pd.read_excel(r'D:\Ynby\Doc\Demo/AKI数据_Refine_尿量_列名去空格.xlsx')

#去除重复列
for colId in range(AKI_Df.shape[1]-1, -1, -1):
    if AKI_Df.columns.values[colId].find('.1') > 0:
        AKI_Df.drop(AKI_Df.columns.values[colId], axis=1, inplace=True)

int64colIds = []
int64colNamess = []
for colId in range(len(AKI_Df.columns)):
    if AKI_Df.dtypes[colId] == np.dtype('int64'):
        int64colIds = int64colIds + [colId]
        int64colNamess = int64colIds + [AKI_Df.columns[colId]]
        print(colId, AKI_Df.columns[colId], AKI_Df.dtypes[colId])

float64colIds = []
float64colNamess = []
for colId in range(len(AKI_Df.columns)):
    if AKI_Df.dtypes[colId] == np.dtype('float64'):
        float64colIds = float64colIds + [colId]
        float64colNamess = float64colNamess + [AKI_Df.columns[colId]]
        print(colId, AKI_Df.columns[colId], AKI_Df.dtypes[colId])

objectcolIds = []
objectcolNamess = []
for colId in range(len(AKI_Df.columns)):
    if AKI_Df.dtypes[colId] == np.dtype('O'):
        objectcolIds = objectcolIds + [colId]
        objectcolNamess = objectcolNamess + [AKI_Df.columns[colId]]
        print(colId, AKI_Df.columns[colId], AKI_Df.dtypes[colId])

shouldBeStrColNames = [eachColName.replace(" ", "") for eachColName in ['分中心单位', '转入科室', 'AKI诊断标准', '入ICU诊断', '手术名称', '手术部位', '1原因', '随访时间（28天）1原因', '随访时间（90天）1原因', '随访时间（1年）1原因']]
shouldBeIntColNames = [eachColName.replace(" ", "") for eachColName in ['血管活性药（肾上腺素，去甲肾上腺素，多巴胺，垂体后叶素，间羟胺）', '氨基糖苷类（庆大霉素，阿米卡星，依替米星，奈替米星）', \
                       '急诊手术', '术中出血（ml）', '术中低血压（有无）', '总入量（ml）', '总出量（ml）', '0.9%氯化钠，乳酸钠林格氏液，醋酸钠林格氏液（ml）', '羟乙基淀粉，明胶，右旋糖酐（ml）',  \
                       '20%白蛋白（ml）', '红细胞（ml）', '血浆（ml）', '血小板（ml）', '入ICU前/基线-肾替代治疗（1/0）', '入ICU前/基线-1（1/0）','入ICU第1天（即刻）-肾替代治疗（1/0）',  \
                       '入ICU第1天（即刻）-1（1/0）', '入ICU 第2天-肾替代治疗（1/0）', '入ICU 第3天-肾替代治疗（1/0）', '入ICU第 4天-肾替代治疗（1/0）', '入ICU第 5天-肾替代治疗（1/0）',  '入ICU第 5天-1（1/0）',  \
                       '入ICU第6天-肾替代治疗（1/0）', '入ICU 第7天-肾替代治疗（1/0）', '入ICU第14天-肾替代治疗（1/0）', '入ICU第14天-1（1/0）', '出院前-肾替代治疗（1/0）', '出院前-1（1/0）', \
                       '出院转归', 'ICU住院时间(天)', '住院时间（天）']]

shouldBeFloatColNames = [eachColName.replace(" ", "") for eachColName in ['身高', '体重', 'P02/Fi02', '乳酸(mmol/L)', '血红蛋白（g/L）', 'ALT(U/L)', 'AST(U/L)', '总蛋白(g/L)', '白蛋白（g/L）', '总胆红素(μmol/L)', '直接胆红素(μmol/L)', \
                         '钾(mmol/L)', '钠(mmol/L)', '氯(mmol/L)', 'D-Dimer(ng/ml)', '肌钙蛋白（TNI）（ng/ml）', 'B型脑钠肽（BNP）（pg/ml）', '降钙素原（ng/ml）',  \
                         'C-反应蛋白（mg/L）', '手术时间（h）', '入ICU前/基线-血肌酐（μmol/L）', '入ICU前/基线-24小时尿量（ml）',  '入ICU第1天（即刻）-24小时尿量（ml）', '入ICU 第2天-24小时尿量（ml）', '入ICU 第3天-血肌酐（μmol/L）', \
                         '入ICU 第3天-24小时尿量（ml）', '入ICU第 4天-血肌酐（μmol/L）', '入ICU第 4天-24小时尿量（ml）', '入ICU第 5天-24小时尿量（ml）', '入ICU第6天-24小时尿量（ml）',   \
                         '入ICU 第7天-血肌酐（μmol/L）', '入ICU 第7天-24小时尿量（ml）', '入ICU第14天-血肌酐（μmol/L）', '入ICU第14天-24小时尿量（ml）', '出院前-24小时尿量（ml）',  \
                         ]]

for eachColName in shouldBeIntColNames + shouldBeFloatColNames:
    if AKI_Df[eachColName].dtypes != np.dtype('O'):
        continue
    colId = np.where(AKI_Df.columns == eachColName)[0]

    for rowId in range(len(AKI_Df)):
        if AKI_Df[eachColName].iloc[rowId] is not np.nan:
            if type(AKI_Df[eachColName].iloc[rowId]) != type('str'):
                continue
            if AKI_Df[eachColName].iloc[rowId].find("（") > 0:
                nums = re.findall(r'\d+', AKI_Df[eachColName].iloc[rowId])
                # a = AKI_Df[eachColName].iloc[rowId].str.split("（")[0]
                # b = AKI_Df[eachColName].iloc[rowId].str.split("（")[1]
                if len(nums) == 2:
                    AKI_Df.iloc[rowId, colId] = np.nan
                    # AKI_Df.iloc[rowId, colId] = round(int(nums[0]) * 24/ int(nums[1]), 2)
            elif AKI_Df[eachColName].iloc[rowId].find("(") > 0:
                nums = re.findall(r'\d+', AKI_Df[eachColName].iloc[rowId])
                # a = AKI_Df[eachColName].iloc[rowId].str.split("（")[0]
                # b = AKI_Df[eachColName].iloc[rowId].str.split("（")[1]
                if len(nums) == 2:
                    AKI_Df.iloc[rowId, colId] = np.nan
                    # AKI_Df.iloc[rowId, colId] = round(int(nums[0]) * 24 / int(nums[1]), 2)
            elif AKI_Df[eachColName].iloc[rowId].find("/") > 0:
                nums = re.findall(r'\d+', AKI_Df[eachColName].iloc[rowId])
                if len(nums) == 2:
                    AKI_Df.iloc[rowId, colId] = np.nan
                    # AKI_Df.iloc[rowId, colId] = round(int(nums[0]) * 24/ int(nums[1]), 2)

    if eachColName.find('1/0') >0 :
        for rowId in range(len(AKI_Df)):
            if AKI_Df[eachColName].iloc[rowId] > 0:
                AKI_Df.iloc[rowId, colId] = 1


shouldBeDateColNames = [eachColName.replace(" ", "") for eachColName in ['入ICU时间', '出ICU时间', '入院时间', '出院时间', '随访时间（28天）', '记录时间']]

for eachColName in shouldBeStrColNames + shouldBeDateColNames:
    colId = np.where(AKI_Df.columns == eachColName)[0][0]
    AKI_Df[eachColName] = AKI_Df[eachColName].astype('str')
    for rowId in range(len(AKI_Df)):
        if AKI_Df.iloc[rowId, colId] is not np.nan:
            AKI_Df.iloc[rowId, colId] = AKI_Df.iloc[rowId, colId].strip()


AKI_Df.to_csv(r'D:\Ynby\Doc\Demo/AKI数据_清洗干净.csv', encoding="UTF-8", na_rep="")
AKI_Df.to_excel(r'D:\Ynby\Doc\Demo/AKI数据_清洗干净.xlsx', encoding="UTF-8", na_rep="")

#分类型变量数字化

DiagnoseTypes = []
import re
pattern = r' |,|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|（|）'

for rowId in range(len(AKI_Df)):
    result_list = re.split(pattern, AKI_Df['入ICU诊断'].iloc[rowId])
    DiagnoseTypes = DiagnoseTypes + result_list

DiagnoseTypeCount = pd.Series(DiagnoseTypes).value_counts()
DiagnoseTypeCount1 = DiagnoseTypeCount[DiagnoseTypeCount.index.values > '9']
DiagnoseTypeCount2 = DiagnoseTypeCount[DiagnoseTypeCount.index.values < '0']
DiagnoseTypeCount = DiagnoseTypeCount1[DiagnoseTypeCount1 > 30]

for eachDiagnoseColId in range(len(DiagnoseTypeCount)):
    AKI_Df[DiagnoseTypeCount.index.values[eachDiagnoseColId]] = 0

for eachDiagnoseColId in range(len(DiagnoseTypeCount)):
    colId = np.where(AKI_Df.columns == DiagnoseTypeCount.index.values[eachDiagnoseColId])[0][0]
    for rowId in range(len(AKI_Df)):
        if AKI_Df['入ICU诊断'].iloc[rowId].find(DiagnoseTypeCount.index.values[eachDiagnoseColId]) > 0:
            AKI_Df.iloc[rowId, colId] = 1


AKI_Df['复发恢复类别'] = np.nan
colId = np.where(AKI_Df.columns == '复发恢复类别')[0][0]
RecoveryTypeDict = {'恢复':0, "复发恢复":1, "复发未恢复":2, "未恢复":3}
for rowId in range(len(AKI_Df)):
    if np.isnan(AKI_Df['逆转时间'][rowId]) == False:
        AKI_Df.iloc[rowId, colId] = 0
    elif AKI_Df['复发恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 1
    elif AKI_Df['复发未恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 2
    elif AKI_Df['未恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 3


AKI_Df.to_csv(r'D:\Ynby\Doc\Demo/AKI数据_清洗干净_分类.csv', encoding="UTF-8", na_rep="", index=False)
AKI_Df.to_excel(r'D:\Ynby\Doc\Demo/AKI数据_清洗干净_分类.xlsx', encoding="UTF-8", na_rep="", index=False)




