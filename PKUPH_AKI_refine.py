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

for colId in range(len(AKI_Df.columns)):
    if AKI_Df.dtypes[colId] == np.dtype('O'):
        AKI_Df[AKI_Df.columns[colId]] = AKI_Df[AKI_Df.columns[colId]].astype('str')
        for rowId in range(len(AKI_Df)):
            if AKI_Df.iloc[rowId, colId] is not np.nan:
                AKI_Df.iloc[rowId, colId] = AKI_Df.iloc[rowId, colId].strip()
                if AKI_Df.iloc[rowId, colId] == 'nan':
                    AKI_Df.iloc[rowId, colId] = ''

shouldBeStrColNames = [eachColName.replace(" ", "") for eachColName in ['分中心单位', '转入科室', 'AKI诊断标准', '入ICU诊断', '手术名称', '手术部位', '1原因', '随访时间（28天）1原因', '随访时间（90天）1原因', '随访时间（1年）1原因']]
shouldBeIntColNames = [eachColName.replace(" ", "") for eachColName in ['血管活性药（肾上腺素，去甲肾上腺素，多巴胺，垂体后叶素，间羟胺）', '氨基糖苷类（庆大霉素，阿米卡星，依替米星，奈替米星）', \
                       '急诊手术', '术中出血（ml）', '术中低血压（有无）', '总入量（ml）', '总出量（ml）', '0.9%氯化钠，乳酸钠林格氏液，醋酸钠林格氏液（ml）', '羟乙基淀粉，明胶，右旋糖酐（ml）',  \
                       '20%白蛋白（ml）', '红细胞（ml）', '血浆（ml）', '血小板（ml）', '入ICU前/基线-肾替代治疗（1/0）', '入ICU前/基线-1（1/0）','入ICU第1天（即刻）-肾替代治疗（1/0）',  \
                       '入ICU第1天（即刻）-1（1/0）', '入ICU 第2天-肾替代治疗（1/0）', '入ICU 第3天-肾替代治疗（1/0）', '入ICU第 4天-肾替代治疗（1/0）', '入ICU第 5天-肾替代治疗（1/0）',  '入ICU第 5天-1（1/0）',  \
                       '入ICU第6天-肾替代治疗（1/0）', '入ICU 第7天-肾替代治疗（1/0）', '入ICU第14天-肾替代治疗（1/0）', '入ICU第14天-1（1/0）', '出院前-肾替代治疗（1/0）', '出院前-1（1/0）', \
                       '出院转归', 'ICU住院时间(天)', '住院时间（天）']]

shouldBeFloatColNames = [eachColName.replace(" ", "") for eachColName in ['身高', '体重', 'P02/Fi02', '乳酸(mmol/L)', '血红蛋白（g/L）', 'ALT(U/L)', 'AST(U/L)', '总蛋白(g/L)', '白蛋白（g/L）', '总胆红素(μmol/L)', '直接胆红素(μmol/L)', \
                         '钾(mmol/L)', '钠(mmol/L)', '氯(mmol/L)', 'D-Dimer(ng/ml)', '肌钙蛋白（TNI）（ng/ml）', 'B型脑钠肽（BNP）（pg/ml）', '降钙素原（ng/ml）',  \
                         'C-反应蛋白（mg/L）', '手术时间（h）',
                         ] + [str for str in AKI_Df.columns.values if str.find('24小时尿量') > 0]   \
                         + [str for str in AKI_Df.columns.values if str.find('血肌酐') > 0]   \
                         ]

for eachColName in shouldBeIntColNames + shouldBeFloatColNames:
    if AKI_Df[eachColName].dtypes != np.dtype('O'):
        continue
    colId = np.where(AKI_Df.columns == eachColName)[0][0]
    for rowId in range(len(AKI_Df)):
        if AKI_Df[eachColName].iloc[rowId] is not np.nan:
            if type(AKI_Df[eachColName].iloc[rowId]) != type('str'):
                continue
            if AKI_Df[eachColName].iloc[rowId].find("（") >= 0:
                nums = re.findall(r'\d+', AKI_Df[eachColName].iloc[rowId])
                # a = AKI_Df[eachColName].iloc[rowId].str.split("（")[0]
                # b = AKI_Df[eachColName].iloc[rowId].str.split("（")[1]
                if len(nums) >= 2:
                    AKI_Df.iloc[rowId, colId] = np.nan
                    # AKI_Df.iloc[rowId, colId] = round(int(nums[0]) * 24/ int(nums[1]), 2)
            elif AKI_Df[eachColName].iloc[rowId].find("(") >= 0:
                nums = re.findall(r'\d+', AKI_Df[eachColName].iloc[rowId])
                if len(nums) >= 2:
                    AKI_Df.iloc[rowId, colId] = np.nan
            elif AKI_Df[eachColName].iloc[rowId].find("/") >= 0:
                nums = re.findall(r'\d+', AKI_Df[eachColName].iloc[rowId])
                if len(nums) >= 2:
                    AKI_Df.iloc[rowId, colId] = np.nan
            elif AKI_Df[eachColName].iloc[rowId].find(" ") >= 0:
                nums = re.findall(r'\d+', AKI_Df[eachColName].iloc[rowId])
                if len(nums) >= 2:
                    AKI_Df.iloc[rowId, colId] = np.nan
            elif AKI_Df[eachColName].iloc[rowId] == "":
                AKI_Df.iloc[rowId, colId] = np.nan

    if eachColName.find('1/0') >0 :
        if AKI_Df[eachColName].dtypes == np.dtype('O'):
            eachColData = []
            for rowId in range(len(AKI_Df)):
                if AKI_Df[eachColName].iloc[rowId] is np.nan:
                    eachColData = eachColData + [np.nan]
                    continue
                if AKI_Df[eachColName].iloc[rowId] == "":
                    eachColData = eachColData + [np.nan]
                elif AKI_Df[eachColName].iloc[rowId] > "0":
                    eachColData = eachColData + [1]
                else:
                    eachColData = eachColData + [0]
            AKI_Df[eachColName] = eachColData
        else:
            for rowId in range(len(AKI_Df)):
                if AKI_Df[eachColName].iloc[rowId] > 0:
                    AKI_Df.iloc[rowId, colId] = 1

shouldBeDateColNames = [eachColName.replace(" ", "") for eachColName in ['入ICU时间', '出ICU时间', '入院时间', '出院时间', '随访时间（28天）', '记录时间']]

# for eachColName in shouldBeStrColNames + shouldBeDateColNames:
#     colId = np.where(AKI_Df.columns == eachColName)[0][0]
#     AKI_Df[eachColName] = AKI_Df[eachColName].astype('str')
#     for rowId in range(len(AKI_Df)):
#         if AKI_Df.iloc[rowId, colId] is not np.nan:
#             AKI_Df.iloc[rowId, colId] = AKI_Df.iloc[rowId, colId].strip()


# AKI_Df.to_csv(r'D:\Ynby\Doc\Demo/AKI数据_清洗干净.csv', encoding="UTF-8", na_rep="")
# AKI_Df.to_excel(r'D:\Ynby\Doc\Demo/AKI数据_清洗干净.xlsx', encoding="UTF-8", na_rep="")

#分类型变量数字化

#入ICU第1~7天（即刻）-肾替代治疗（1/0）， 合并为1列，只要有1个1，就是1
allTouxiColumns = [str for str in AKI_Df.columns.values if str.find('肾替代治疗') > 0 ]
AKI_Df['肾替代治疗（1/0）'] = np.nan
colId = np.where(AKI_Df.columns == '肾替代治疗（1/0）')[0][0]
for rowId in range(len(AKI_Df)):
    for eachcolId in allTouxiColumns:
        found = False
        if AKI_Df[eachcolId].iloc[rowId] == 1:
            flagvalue = 1
            found = True
            break
        elif AKI_Df[eachcolId].iloc[rowId] == 0:
            flagvalue = 0
            found = True

    if found == True:
        AKI_Df.iloc[rowId, colId] = flagvalue


    if np.isnan(AKI_Df['逆转时间'][rowId]) == False:
        AKI_Df.iloc[rowId, colId] = 0
    elif AKI_Df['复发恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 1
    elif AKI_Df['复发未恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 2
    elif AKI_Df['未恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 3


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

AKI_Df['复发恢复二分类'] = np.nan
colId = np.where(AKI_Df.columns == '复发恢复二分类')[0][0]
RecoveryTypeDict = {'恢复':0, "复发恢复":1, "复发未恢复":2, "未恢复":3}
for rowId in range(len(AKI_Df)):
    if np.isnan(AKI_Df['逆转时间'][rowId]) == False:
        AKI_Df.iloc[rowId, colId] = 0
    elif AKI_Df['复发恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 1
    elif AKI_Df['复发未恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 1
    elif AKI_Df['未恢复'][rowId] == 1:
        AKI_Df.iloc[rowId, colId] = 1


AKI_Df.to_csv(r'D:\Ynby\Doc\Demo/AKI数据_已清洗_二分类.csv', encoding="UTF-8", na_rep="", index=False)
AKI_Df.to_excel(r'D:\Ynby\Doc\Demo/AKI数据_已清洗_二分类.xlsx', encoding="UTF-8", na_rep="", index=False)

AKI_Df['入ICU第7天-24小时尿量（ml）'].astype('float64')

AKI_Df_recovery = AKI_Df[np.isnan(AKI_Df['逆转时间']) == False]
AKI_Df_recovery.to_csv(r'D:\Ynby\Doc\Demo/AKI数据_已清洗_恢复时间.csv', encoding="UTF-8", na_rep="", index=False)
AKI_Df_recovery.to_excel(r'D:\Ynby\Doc\Demo/AKI数据_已清洗_恢复时间.xlsx', encoding="UTF-8", na_rep="", index=False)

#
# create table AKI数据_清洗干净_分类
# (
#     病历号                                       INTEGER,
#     分中心单位                                     VARCHAR(200),
#     年龄                                        INTEGER,
#     性别                                        INTEGER,
#     身高                                        FLOAT,
#     体重                                        FLOAT,
#     转入科室                                      VARCHAR(200),
#     入ICUAPACHEII评分                            INTEGER,
#     入ICUSOFA评分                                INTEGER,
#     "入ICU即刻生命体征心率(次/分)"                       FLOAT,
#     "入ICU即刻生命体征收缩压(mmHg)"                     FLOAT,
#     "入ICU即刻生命体征舒张压(mmHg)"                     FLOAT,
#     入ICU诊断                                    VARCHAR(200),
#     AKI诊断标准                                   VARCHAR(200),
#     高血压                                       INTEGER,
#     糖尿病                                       INTEGER,
#     高脂血症                                      INTEGER,
#     心脏病                                       INTEGER,
#     肺部疾病                                      INTEGER,
#     肝脏病史                                      INTEGER,
#     慢性肾病史                                     INTEGER,
#     卒中                                        INTEGER,
#     恶性肿瘤                                      INTEGER,
#     "P02/Fi02"                                FLOAT,
#     "乳酸(mmol/L)"                              FLOAT,
#     "血红蛋白（g/L）"                               FLOAT,
#     "ALT(U/L)"                                FLOAT,
#     "AST(U/L)"                                FLOAT,
#     "总蛋白(g/L)"                                FLOAT,
#     "白蛋白（g/L）"                                FLOAT,
#     "尿素（mmol/L）"                              FLOAT,
#     "肌酐(μmol/L)"                              FLOAT,
#     "尿酸(mmol/L)"                              FLOAT,
#     "总胆红素(μmol/L)"                            FLOAT,
#     "直接胆红素(μmol/L)"                           FLOAT,
#     "钾(mmol/L)"                               FLOAT,
#     "钠(mmol/L)"                               FLOAT,
#     "氯(mmol/L)"                               FLOAT,
#     "PT(s)"                                   FLOAT,
#     "APTT(s)"                                 FLOAT,
#     "FIB(mg/dl)"                              FLOAT,
#     "D-Dimer(ng/ml)"                          FLOAT,
#     "肌钙蛋白（TNI）（ng/ml）"                        FLOAT,
#     "B型脑钠肽（BNP）（pg/ml）"                       FLOAT,
#     "降钙素原（ng/ml）"                             FLOAT,
#     "C-反应蛋白（mg/L）"                            FLOAT,
#     血管活性药（肾上腺素，去甲肾上腺素，多巴胺，垂体后叶素，间羟胺）          FLOAT,
#     氨基糖苷类（庆大霉素，阿米卡星，依替米星，奈替米星）                FLOAT,
#     "碳青霉烯类（亚胺培南/西司他丁，美罗培南，厄他培南）"              FLOAT,
#     喹诺酮类（诺氟沙星，氧氟沙星，左氧氟沙星，环丙沙星，莫西沙星）           FLOAT,
#     硝基咪唑类（甲硝唑，奥硝唑，替硝唑）                        FLOAT,
#     青霉素类（青霉素，苯唑西林，美洛西林，哌拉西林，哌拉西林舒巴坦，哌拉西林他唑巴坦） FLOAT,
#     头孢菌素类（头孢呋辛，头孢曲松，头孢他啶，头孢哌酮，头孢吡肟）           FLOAT,
#     两性霉素B（两性霉素B，两性霉素B脂质体）                     FLOAT,
#     万古霉素（万古霉素，去甲万古霉素）                         FLOAT,
#     "造影剂(泛影葡胺，欧乃派克，碘海醇，碘克沙醇)"                 FLOAT,
#     利尿剂（呋塞米，托拉塞米，螺内酯，丁脲胺，布美他尼）                FLOAT,
#     甘露醇                                       FLOAT,
#     手术                                        FLOAT,
#     手术名称                                      VARCHAR(200),
#     手术部位                                      VARCHAR(200),
#     急诊手术                                      FLOAT,
#     手术时间（H）                                   FLOAT,
#     术中出血（ML）                                  FLOAT,
#     术中低血压（有无）                                 FLOAT,
#     总入量（ML）                                   FLOAT,
#     总出量（ML）                                   FLOAT,
#     "0.9%氯化钠，乳酸钠林格氏液，醋酸钠林格氏液（ml）"             FLOAT,
#     羟乙基淀粉，明胶，右旋糖酐（ML）                         FLOAT,
#     "20%白蛋白（ml）"                              FLOAT,
#     红细胞（ML）                                   FLOAT,
#     血浆（ML）                                    FLOAT,
#     血小板（ML）                                   FLOAT,
#     "入ICU前/基线-血肌酐（μmol/L）"                    FLOAT,
#     "入ICU前/基线-24小时尿量（ml）"                     VARCHAR(200),
#     "入ICU前/基线-肾替代治疗（1/0）"                     FLOAT,
#     "入ICU前/基线-1（1/0）"                         FLOAT,
#     "入ICU第1天（即刻）-血肌酐（μmol/L）"                 FLOAT,
#     "入ICU第1天（即刻）-24小时尿量（ml）"                  VARCHAR(200),
#     "入ICU第1天（即刻）-肾替代治疗（1/0）"                  VARCHAR(200),
#     "入ICU第1天（即刻）-1（1/0）"                      INTEGER,
#     "入ICU第2天-血肌酐（μmol/L）"                     FLOAT,
#     "入ICU第2天-24小时尿量（ml）"                      VARCHAR(200),
#     "入ICU第2天-肾替代治疗（1/0）"                      VARCHAR(200),
#     "入ICU第2天-1（1/0）"                          FLOAT,
#     "入ICU第3天-血肌酐（μmol/L）"                     FLOAT,
#     "入ICU第3天-24小时尿量（ml）"                      VARCHAR(200),
#     "入ICU第3天-肾替代治疗（1/0）"                      VARCHAR(200),
#     "入ICU第3天-1（1/0）"                          FLOAT,
#     "入ICU第4天-血肌酐（μmol/L）"                     FLOAT,
#     "入ICU第4天-24小时尿量（ml）"                      VARCHAR(200),
#     "入ICU第4天-肾替代治疗（1/0）"                      VARCHAR(200),
#     "入ICU第4天-1（1/0）"                          FLOAT,
#     "入ICU第5天-血肌酐（μmol/L）"                     FLOAT,
#     "入ICU第5天-24小时尿量（ml）"                      VARCHAR(200),
#     "入ICU第5天-肾替代治疗（1/0）"                      VARCHAR(200),
#     "入ICU第5天-1（1/0）"                          FLOAT,
#     "入ICU第6天-血肌酐（μmol/L）"                     FLOAT,
#     "入ICU第6天-24小时尿量（ml）"                      VARCHAR(200),
#     "入ICU第6天-肾替代治疗（1/0）"                      VARCHAR(200),
#     "入ICU第6天-1（1/0）"                          FLOAT,
#     "入ICU第7天-血肌酐（μmol/L）"                     FLOAT,
#     "入ICU第7天-24小时尿量（ml）"                      VARCHAR(200),
#     "入ICU第7天-肾替代治疗（1/0）"                      VARCHAR(200),
#     "入ICU第7天-1（1/0）"                          FLOAT,
#     "入ICU第14天-血肌酐（μmol/L）"                    FLOAT,
#     "入ICU第14天-24小时尿量（ml）"                     VARCHAR(200),
#     "入ICU第14天-肾替代治疗（1/0）"                     VARCHAR(200),
#     "入ICU第14天-1（1/0）"                         FLOAT,
#     "出院前-血肌酐（μmol/L）"                         FLOAT,
#     "出院前-24小时尿量（ml）"                          VARCHAR(200),
#     "出院前-肾替代治疗（1/0）"                          VARCHAR(200),
#     "出院前-1（1/0）"                              FLOAT,
#     出院转归                                      FLOAT,
#     "1原因"                                     VARCHAR(200),
#     入ICU时间                                    TIMESTAMP(6),
#     出ICU时间                                    TIMESTAMP(6),
#     "ICU住院时间(天)"                              FLOAT,
#     入院时间                                      TIMESTAMP(6),
#     出院时间                                      TIMESTAMP(6),
#     住院时间（天）                                   FLOAT,
#     随访时间（28天）                                 VARCHAR(200),
#     随访时间（28天）101                              FLOAT,
#     随访时间（28天）1原因                              VARCHAR(200),
#     随访时间（90天）                                 VARCHAR(200),
#     随访时间（90天）101                              FLOAT,
#     随访时间（90天）1原因                              VARCHAR(200),
#     随访时间（1年）                                  VARCHAR(200),
#     随访时间（1年）101                               FLOAT,
#     随访时间（1年）1原因                               VARCHAR(200),
#     记录时间                                      VARCHAR(200),
#     逆转时间                                      FLOAT,
#     复发恢复                                      FLOAT,
#     复发未恢复                                     FLOAT,
#     未恢复                                       FLOAT,
#     AKI分期                                     FLOAT,
#     "3个月转归"                                   FLOAT,
#     术后                                        INTEGER,
#     脓毒症休克                                     INTEGER,
#     脓毒症                                       INTEGER,
#     ARDS                                      INTEGER,
#     肺栓塞                                       INTEGER,
#     甲亢危象                                      INTEGER,
#     肾上腺危象                                     INTEGER,
#     糖尿病酮症酸中毒                                  INTEGER,
#     哮喘                                        INTEGER,
#     急性心肌梗死                                    INTEGER,
#     急性心力衰竭                                    INTEGER,
#     心包填塞                                      INTEGER,
#     脑卒中                                       INTEGER,
#     重度颅脑损伤                                    INTEGER,
#     出血性休克                                     INTEGER,
#     大出血                                       INTEGER,
#     高血压病                                      INTEGER,
#     肾衰竭                                       INTEGER,
#     复发恢复类别                                    INTEGER
# )
#     organize by row;
#
