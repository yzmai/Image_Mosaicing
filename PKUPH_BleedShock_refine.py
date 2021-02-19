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

BleedShock_Df.rename(columns= {'手术部位腹部手术=1，胸部手术=2，骨科手术=3，颅脑手术=4，大血管手术=5，周围血管手术=6，颌面部7' : "手术部位"}, inplace=True)

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
        BleedShock_Df[BleedShock_Df.columns[colId]] = np.round(BleedShock_Df[BleedShock_Df.columns[colId]], 1)
        print(colId, BleedShock_Df.columns[colId], BleedShock_Df.dtypes[colId])

objectcolIds = []
objectcolNamess = []
for colId in range(len(BleedShock_Df.columns)):
    if BleedShock_Df.dtypes[colId] == np.dtype('O'):
        objectcolIds = objectcolIds + [colId]
        objectcolNamess = objectcolNamess + [BleedShock_Df.columns[colId]]
        eachstrcol = BleedShock_Df[BleedShock_Df.columns[colId]].astype(np.str)
        eachstrcol = [eachstr.strip() for eachstr in eachstrcol]
        BleedShock_Df[BleedShock_Df.columns[colId]] = eachstrcol
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

sexCol = BleedShock_Df['性别']
sexcolId = np.where(BleedShock_Df.columns == '性别')[0][0]
BleedShock_Df.iloc[[rowId for rowId in np.where(sexCol == '男')[0]], sexcolId] = 1
BleedShock_Df.iloc[[rowId for rowId in np.where(sexCol == '女')[0]], sexcolId] = 2


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

BleedShock_Df = BleedShock_Df.replace(np.nan, '', regex=True)

BleedShock_Df.to_csv(r'D:\Ynby\Doc\Demo/出血性休克数据_清洗干净_分类.csv', encoding="UTF-8", na_rep='', index=False)
BleedShock_Df.to_excel(r'D:\Ynby\Doc\Demo/出血性休克数据_清洗干净_分类.xlsx', encoding="UTF-8", na_rep='', index=False)




# -- auto-generated definition
# create table 出血性休克数据_清洗干净_分类
# (
#     病史ID                                      VARCHAR(80),
#     性别                                        INTEGER,
#     就诊年龄                                      INTEGER,
#     出院诊断                                      VARCHAR(5000),
#     主诉                                        VARCHAR(5000),
#     现病史                                       VARCHAR(5000),
#     抗凝药及抗血小板药史                                INTEGER,
#     当前吸烟                                      INTEGER,
#     当前饮酒                                      INTEGER,
#     过敏史                                       INTEGER,
#     "脑卒中是=1，否=0"                              INTEGER,
#     冠心病                                       INTEGER,
#     高血压                                       INTEGER,
#     慢性肺病                                      INTEGER,
#     糖尿病                                       INTEGER,
#     "慢性肾功能不全/衰竭"                              INTEGER,
#     恶性肿瘤                                      INTEGER,
#     受伤原因（坠落伤1，车祸伤2，跌倒3，砸伤4，刺伤5，动物咬伤6等）        INTEGER,
#     受伤类型（钝挫伤1，刺伤2，烧伤3）                        INTEGER,
#     主要出血部位                                    VARCHAR(400),
#     主要出血部位（胸部1，腹部2，骨盆3，四肢4，血管5，颅脑6，会阴区7）      INTEGER,
#     受伤到入院时间H                                  DECIMAL(4, 1),
#     "身高(cm)"                                  DECIMAL(5, 1),
#     "体重(kg)"                                  DECIMAL(5, 1),
#     入院收缩压                                     DECIMAL(5, 1),
#     舒张压                                       DECIMAL(4, 1),
#     心率                                        INTEGER,
#     呼吸                                        INTEGER,
#     体温                                        DECIMAL(4, 1),
#     是否手术                                      INTEGER,
#     入院时间                                      TIMESTAMP(6),
#     手术开始时间（几点几分）                              TIMESTAMP(6),
#     手术结束时间                                    TIMESTAMP(6),
#     入院到手术时间H                                  DECIMAL(5, 2),
#     手术时间H                                     DECIMAL(4, 2),
#     急诊手术                                      DECIMAL(3, 1),
#     手术名称                                      VARCHAR(1000),
#     入院后输红细胞量（U）首页                             DECIMAL(6, 1),
#     输血浆量（ML）                                  DECIMAL(5, 1),
#     血小板ML                                     DECIMAL(5, 1),
#     氨甲环酸                                      INTEGER,
#     是否血管活性药                                   INTEGER,
#     血管活性药物去甲肾上腺素1、多巴胺2、肾上腺素3、间羟胺4、异丙肾5        VARCHAR(400),
#     开始时间                                      TIMESTAMP(6),
#     结束时间                                      TIMESTAMP(6),
#     使用时间H                                     DECIMAL(6, 2),
#     ARDS                                      DECIMAL(3, 1),
#     肺栓塞                                       DECIMAL(3, 1),
#     心肌损伤                                      DECIMAL(3, 1),
#     心肌梗死                                      DECIMAL(3, 1),
#     心力衰竭                                      DECIMAL(3, 1),
#     急性肾损伤                                     DECIMAL(3, 1),
#     肝损伤                                       DECIMAL(3, 1),
#     凝血功能障碍                                    DECIMAL(3, 1),
#     神经系统卒中                                    DECIMAL(3, 1),
#     感染                                        DECIMAL(3, 1),
#     感染部位                                      VARCHAR(800),
#     静脉血栓                                      DECIMAL(3, 1),
#     骨筋膜室综合症                                   INTEGER,
#     出院转归                                      VARCHAR(400),
#     "死亡原因，1=颅脑损伤，2=心脏事件。3=出血性休克.4=感染,5=急性脑梗死" INTEGER,
#     出院时间                                      TIMESTAMP(6),
#     住院天数                                      INTEGER,
#     呼吸机使用时间                                   DECIMAL(5, 1),
#     "入ICU时间-1"                                TIMESTAMP(6),
#     "出ICU时间-1"                                TIMESTAMP(6),
#     住ICU时间D                                   DECIMAL(4, 1),
#     费用                                        DECIMAL(9, 2),
#     入院白细胞计数                                   DECIMAL(5, 2),
#     入院中性粒细胞计数                                 DECIMAL(5, 2),
#     入院淋巴细胞计数                                  DECIMAL(4, 2),
#     入院血红蛋白                                    DECIMAL(5, 1),
#     入院血小板计数                                   DECIMAL(5, 1),
#     "入院钾(mmol/L)"                             DECIMAL(4, 2),
#     "入院钠(mmol/L)"                             DECIMAL(5, 1),
#     "入院氯(mmol/L)"                             DECIMAL(5, 1),
#     "入院钙(mmol/L)"                             DECIMAL(4, 2),
#     入院葡萄糖                                     DECIMAL(5, 2),
#     "入院谷丙转氨酶(U/L)"                            DECIMAL(5, 1),
#     "入院谷草转氨入院酶(U/L)"                          DECIMAL(5, 1),
#     "入院总蛋白(g/L)"                              DECIMAL(4, 1),
#     "入院白蛋白（g/L）"                              DECIMAL(4, 1),
#     "入院尿素（mmol/L）"                            DECIMAL(5, 2),
#     "入院血肌酐(μmol/L)"                           DECIMAL(5, 1),
#     "入院估算肾小球滤过率(ml/min)"                      DECIMAL(6, 2),
#     "入院尿酸(mmol/L)"                            DECIMAL(5, 1),
#     "入院总胆红素(μmol/L)"                          DECIMAL(4, 1),
#     "入院直接胆红素(μmol/L)"                         DECIMAL(4, 1),
#     入院CK                                      DECIMAL(7, 1),
#     "入院凝血酶原时间(s)"                             DECIMAL(4, 1),
#     "入院活化部分凝血活酶时间(s)"                         DECIMAL(5, 1),
#     "入院纤维蛋白原(mg/dl)"                          DECIMAL(5, 1),
#     "入院D二聚体(ng/ml)"                           DECIMAL(7, 1),
#     "入院肌钙蛋白（TNI）（ng/ml）肌钙蛋白（TNI）（ng/ml）"      DECIMAL(20, 18),
#     "入院肌钙蛋白（TNI）（ng/ml）B型脑钠肽（BNP）（pg/ml）"     DECIMAL(6, 1),
#     "入院C-反应蛋白（mg/L）"                          DECIMAL(6, 2),
#     "入院降钙素原（ng/ml）"                           DECIMAL(20, 18),
#     入院酸碱度                                     DECIMAL(18, 16),
#     入院氧分压                                     DECIMAL(5, 1),
#     入院氧浓度                                     DECIMAL(5, 1),
#     入院氧和指数                                    DECIMAL(18, 14),
#     入院二氧化碳分压                                  DECIMAL(4, 1),
#     入院乳酸                                      DECIMAL(4, 1),
#     入院碱剩余                                     DECIMAL(5, 1),
#     入院第2天白细胞计数                                DECIMAL(5, 2),
#     入院第2天中性粒细胞计数                              DECIMAL(5, 2),
#     入院第2天淋巴细胞计数                               DECIMAL(4, 2),
#     入院第2天血红蛋白                                 DECIMAL(5, 1),
#     入院第2天血小板计数                                DECIMAL(5, 1),
#     "入院第2天钾(mmol/L)"                          DECIMAL(4, 2),
#     "入院第2天钠(mmol/L)"                          DECIMAL(5, 1),
#     "入院第2天氯(mmol/L)"                          DECIMAL(5, 1),
#     "入院第2天钙(mmol/L)"                          DECIMAL(4, 2),
#     入院第2天葡萄糖                                  DECIMAL(5, 2),
#     "入院第2天谷丙转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第2天谷草转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第2天总蛋白(g/L)"                           DECIMAL(4, 1),
#     "入院第2天白蛋白（g/L）"                           DECIMAL(4, 1),
#     "入院第2天尿素（mmol/L）"                         DECIMAL(5, 2),
#     "入院第2天血肌酐(μmol/L)"                        DECIMAL(5, 1),
#     "入院第2天估算肾小球滤过率(ml/min)"                   DECIMAL(6, 2),
#     "入院第2天尿酸(mmol/L)"                         DECIMAL(5, 1),
#     "入院第2天总胆红素(μmol/L)"                       DECIMAL(4, 1),
#     "入院第2天直接胆红素(μmol/L)"                      DECIMAL(4, 1),
#     入院第2天CK                                   DECIMAL(6, 1),
#     "入院第2天凝血酶原时间(s)"                          DECIMAL(4, 1),
#     "入院第2天活化部分凝血活酶时间(s)"                      DECIMAL(4, 1),
#     "入院第2天纤维蛋白原(mg/dl)"                       DECIMAL(5, 1),
#     "入院第2天D二聚体(ng/ml)"                        DECIMAL(7, 1),
#     "入院第2天肌钙蛋白（TNI）（ng/ml）"                   DECIMAL(20, 18),
#     "入院第2天B型脑钠肽（BNP）（pg/ml）"                  DECIMAL(6, 1),
#     "入院第2天C-反应蛋白（mg/L）"                       DECIMAL(6, 2),
#     "入院第2天降钙素原（ng/ml）"                        DECIMAL(19, 17),
#     入院第2天酸碱度                                  DECIMAL(18, 16),
#     入院第2天氧分压                                  DECIMAL(5, 1),
#     入院第2天氧浓度                                  DECIMAL(5, 1),
#     入院第2天氧和指数                                 DECIMAL(18, 14),
#     入院第2天二氧化碳分压                               DECIMAL(4, 1),
#     入院第2天乳酸                                   DECIMAL(4, 1),
#     入院第2天碱剩余                                  DECIMAL(4, 1),
#     入院第3天白细胞计数                                DECIMAL(5, 2),
#     入院第3天中性粒细胞计数                              DECIMAL(5, 2),
#     入院第3天淋巴细胞计数                               DECIMAL(4, 2),
#     入院第3天血红蛋白                                 DECIMAL(5, 1),
#     入院第3天血小板计数                                DECIMAL(5, 1),
#     "入院第3天钾(mmol/L)"                          DECIMAL(4, 2),
#     "入院第3天钠(mmol/L)"                          DECIMAL(5, 1),
#     "入院第3天氯(mmol/L)"                          DECIMAL(5, 1),
#     "入院第3天钙(mmol/L)"                          DECIMAL(4, 2),
#     入院第3天葡萄糖                                  DECIMAL(5, 2),
#     "入院第3天谷丙转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第3天谷草转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第3天总蛋白(g/L)"                           DECIMAL(4, 1),
#     "入院第3天白蛋白（g/L）"                           DECIMAL(4, 1),
#     "入院第3天尿素（mmol/L）"                         DECIMAL(5, 2),
#     "入院第3天血肌酐(μmol/L)"                        DECIMAL(5, 1),
#     "入院第3天估算肾小球滤过率(ml/min)"                   DECIMAL(6, 2),
#     "入院第3天尿酸(mmol/L)"                         DECIMAL(5, 1),
#     "入院第3天总胆红素(μmol/L)"                       DECIMAL(5, 1),
#     "入院第3天直接胆红素(μmol/L)"                      DECIMAL(5, 1),
#     入院第3天CK                                   DECIMAL(6, 1),
#     "入院第3天凝血酶原时间(s)"                          DECIMAL(4, 1),
#     "入院第3天活化部分凝血活酶时间(s)"                      DECIMAL(4, 1),
#     "入院第3天纤维蛋白原(mg/dl)"                       DECIMAL(5, 1),
#     "入院第3天D二聚体(ng/ml)"                        DECIMAL(7, 1),
#     "入院第3天肌钙蛋白（TNI）（ng/ml）"                   DECIMAL(20, 18),
#     "入院第3天B型脑钠肽（BNP）（pg/ml）"                  DECIMAL(6, 1),
#     "入院第3天C-反应蛋白（mg/L）"                       DECIMAL(6, 2),
#     "入院第3天降钙素原（ng/ml）"                        DECIMAL(20, 18),
#     入院第3天酸碱度                                  DECIMAL(18, 16),
#     入院第3天氧分压                                  DECIMAL(5, 1),
#     入院第3天氧浓度                                  DECIMAL(5, 1),
#     入院第3天氧和指数                                 DECIMAL(18, 14),
#     入院第3天二氧化碳分压                               DECIMAL(4, 1),
#     入院第3天乳酸                                   DECIMAL(3, 1),
#     入院第3天碱剩余                                  DECIMAL(4, 1),
#     入院第4天白细胞计数                                DECIMAL(5, 2),
#     入院第4天中性粒细胞计数                              DECIMAL(4, 2),
#     入院第4天淋巴细胞计数                               DECIMAL(4, 2),
#     入院第4天血红蛋白                                 DECIMAL(5, 1),
#     入院第4天血小板计数                                DECIMAL(5, 1),
#     "入院第4天钾(mmol/L)"                          DECIMAL(4, 2),
#     "入院第4天钠(mmol/L)"                          DECIMAL(5, 1),
#     "入院第4天氯(mmol/L)"                          DECIMAL(5, 1),
#     "入院第4天钙(mmol/L)"                          DECIMAL(4, 2),
#     入院第4天葡萄糖                                  DECIMAL(5, 2),
#     "入院第4天谷丙转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第4天谷草转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第4天总蛋白(g/L)"                           DECIMAL(4, 1),
#     "入院第4天白蛋白（g/L）"                           DECIMAL(4, 1),
#     "入院第4天尿素（mmol/L）"                         DECIMAL(5, 2),
#     "入院第4天血肌酐(μmol/L)"                        DECIMAL(5, 1),
#     "入院第4天估算肾小球滤过率(ml/min)"                   DECIMAL(6, 2),
#     "入院第4天尿酸(mmol/L)"                         DECIMAL(5, 1),
#     "入院第4天总胆红素(μmol/L)"                       DECIMAL(5, 1),
#     "入院第4天直接胆红素(μmol/L)"                      DECIMAL(5, 1),
#     入院第4天CK                                   DECIMAL(6, 1),
#     "入院第4天凝血酶原时间(s)"                          DECIMAL(4, 1),
#     "入院第4天活化部分凝血活酶时间(s)"                      DECIMAL(4, 1),
#     "入院第4天纤维蛋白原(mg/dl)"                       DECIMAL(5, 1),
#     "入院第4天D二聚体(ng/ml)"                        DECIMAL(7, 1),
#     "入院第4天肌钙蛋白（TNI）（ng/ml）"                   DECIMAL(20, 18),
#     "入院第4天B型脑钠肽（BNP）（pg/ml）"                  DECIMAL(6, 1),
#     "入院第4天C-反应蛋白（mg/L）"                       DECIMAL(6, 2),
#     "入院第4天降钙素原（ng/ml）"                        DECIMAL(5, 3),
#     入院第4天酸碱度                                  DECIMAL(18, 16),
#     入院第4天氧分压                                  DECIMAL(5, 1),
#     入院第4天氧浓度                                  DECIMAL(5, 1),
#     入院第4天氧和指数                                 DECIMAL(18, 14),
#     入院第4天二氧化碳分压                               DECIMAL(4, 1),
#     入院第4天乳酸                                   DECIMAL(3, 1),
#     入院第4天碱剩余                                  DECIMAL(4, 1),
#     入院第5天白细胞计数                                DECIMAL(5, 2),
#     入院第5天中性粒细胞计数                              DECIMAL(5, 2),
#     入院第5天淋巴细胞计数                               DECIMAL(4, 2),
#     入院第5天血红蛋白                                 DECIMAL(5, 1),
#     入院第5天血小板计数                                DECIMAL(5, 1),
#     "入院第5天钾(mmol/L)"                          DECIMAL(4, 2),
#     "入院第5天钠(mmol/L)"                          DECIMAL(5, 1),
#     "入院第5天氯(mmol/L)"                          DECIMAL(5, 1),
#     "入院第5天钙(mmol/L)"                          DECIMAL(4, 2),
#     入院第5天葡萄糖                                  DECIMAL(5, 2),
#     "入院第5天谷丙转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第5天谷草转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第5天总蛋白(g/L)"                           DECIMAL(4, 1),
#     "入院第5天白蛋白（g/L）"                           DECIMAL(4, 1),
#     "入院第5天尿素（mmol/L）"                         DECIMAL(5, 2),
#     "入院第5天血肌酐(μmol/L)"                        DECIMAL(5, 1),
#     "入院第5天估算肾小球滤过率(ml/min)"                   DECIMAL(6, 2),
#     "入院第5天尿酸(mmol/L)"                         DECIMAL(5, 1),
#     "入院第5天总胆红素(μmol/L)"                       DECIMAL(5, 1),
#     "入院第5天直接胆红素(μmol/L)"                      DECIMAL(5, 1),
#     入院第5天CK                                   DECIMAL(6, 1),
#     "入院第5天凝血酶原时间(s)"                          DECIMAL(4, 1),
#     "入院第5天活化部分凝血活酶时间(s)"                      DECIMAL(4, 1),
#     "入院第5天纤维蛋白原(mg/dl)"                       DECIMAL(5, 1),
#     "入院第5天D二聚体(ng/ml)"                        DECIMAL(6, 1),
#     "入院第5天肌钙蛋白（TNI）（ng/ml）"                   DECIMAL(20, 18),
#     "入院第5天B型脑钠肽（BNP）（pg/ml）"                  DECIMAL(6, 1),
#     "入院第5天C-反应蛋白（mg/L）"                       DECIMAL(5, 2),
#     "入院第5天降钙素原（ng/ml）"                        DECIMAL(5, 3),
#     入院第5天酸碱度                                  DECIMAL(17, 15),
#     入院第5天氧分压                                  DECIMAL(5, 1),
#     入院第5天氧浓度                                  DECIMAL(4, 1),
#     入院第5天氧和指数                                 DECIMAL(18, 14),
#     入院第5天二氧化碳分压                               DECIMAL(4, 1),
#     入院第5天乳酸                                   DECIMAL(3, 1),
#     入院第5天碱剩余                                  DECIMAL(4, 1),
#     入院第6天白细胞计数                                DECIMAL(5, 2),
#     入院第6天中性粒细胞计数                              DECIMAL(5, 2),
#     入院第6天淋巴细胞计数                               DECIMAL(4, 2),
#     入院第6天血红蛋白                                 DECIMAL(5, 1),
#     入院第6天血小板计数                                DECIMAL(5, 1),
#     "入院第6天钾(mmol/L)"                          DECIMAL(4, 2),
#     "入院第6天钠(mmol/L)"                          DECIMAL(5, 1),
#     "入院第6天氯(mmol/L)"                          DECIMAL(5, 1),
#     "入院第6天钙(mmol/L)"                          DECIMAL(4, 2),
#     入院第6天葡萄糖                                  DECIMAL(5, 2),
#     "入院第6天谷丙转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第6天谷草转氨酶(U/L)"                         DECIMAL(5, 1),
#     "入院第6天总蛋白(g/L)"                           DECIMAL(4, 1),
#     "入院第6天白蛋白（g/L）"                           DECIMAL(4, 1),
#     "入院第6天尿素（mmol/L）"                         DECIMAL(5, 2),
#     "入院第6天血肌酐(μmol/L)"                        DECIMAL(5, 1),
#     "入院第6天估算肾小球滤过率(ml/min)"                   DECIMAL(6, 2),
#     "入院第6天尿酸(mmol/L)"                         DECIMAL(5, 1),
#     "入院第6天总胆红素(μmol/L)"                       DECIMAL(5, 1),
#     "入院第6天直接胆红素(μmol/L)"                      DECIMAL(4, 1),
#     入院第6天CK                                   DECIMAL(6, 1),
#     "入院第6天凝血酶原时间(s)"                          DECIMAL(4, 1),
#     "入院第6天活化部分凝血活酶时间(s)"                      DECIMAL(4, 1),
#     "入院第6天纤维蛋白原(mg/dl)"                       DECIMAL(5, 1),
#     "入院第6天D二聚体(ng/ml)"                        DECIMAL(7, 1),
#     "入院第6天肌钙蛋白（TNI）（ng/ml）"                   DECIMAL(20, 18),
#     "入院第6天B型脑钠肽（BNP）（pg/ml）"                  DECIMAL(6, 1),
#     "入院第6天C-反应蛋白（mg/L）"                       DECIMAL(5, 2),
#     "入院第6天降钙素原（ng/ml）"                        DECIMAL(19, 17),
#     入院第6天酸碱度                                  DECIMAL(18, 16),
#     入院第6天氧分压                                  DECIMAL(5, 1),
#     入院第6天氧浓度                                  DECIMAL(4, 1),
#     入院第6天氧和指数                                 DECIMAL(18, 14),
#     入院第6天二氧化碳分压                               DECIMAL(4, 1),
#     入院第6天乳酸                                   DECIMAL(3, 1),
#     入院第6天碱剩余                                  DECIMAL(4, 1),
#     入院第7天白细胞计数                                DECIMAL(5, 2),
#     入院第7天中性粒细胞计数                              DECIMAL(4, 2),
#     入院第7天淋巴细胞计数                               DECIMAL(4, 2),
#     入院第7天血红蛋白                                 DECIMAL(5, 1),
#     入院第7天血小板计数                                DECIMAL(5, 1),
#     "入院第7天钾(mmol/L)"                          DECIMAL(4, 2),
#     "入院第7天钠(mmol/L)"                          DECIMAL(5, 1),
#     "入院第7天氯(mmol/L)"                          DECIMAL(5, 1),
#     "入院第7天钙(mmol/L)"                          DECIMAL(4, 2),
#     入院第7天葡萄糖                                  DECIMAL(5, 2),
#     "入院第7天谷丙转氨酶(U/L)"                         DECIMAL(4, 1),
#     "入院第7天谷草转氨酶(U/L)"                         DECIMAL(4, 1),
#     "入院第7天总蛋白(g/L)"                           DECIMAL(4, 1),
#     "入院第7天白蛋白（g/L）"                           DECIMAL(4, 1),
#     "入院第7天尿素（mmol/L）"                         DECIMAL(5, 2),
#     "入院第7天血肌酐(μmol/L)"                        DECIMAL(4, 1),
#     "入院第7天估算肾小球滤过率(ml/min)"                   DECIMAL(6, 2),
#     "入院第7天尿酸(mmol/L)"                         DECIMAL(5, 1),
#     "入院第7天总胆红素(μmol/L)"                       DECIMAL(5, 1),
#     "入院第7天直接胆红素(μmol/L)"                      DECIMAL(5, 1),
#     入院第7天CK                                   DECIMAL(6, 1),
#     "入院第7天凝血酶原时间(s)"                          DECIMAL(4, 1),
#     "入院第7天活化部分凝血活酶时间(s)"                      DECIMAL(4, 1),
#     "入院第7天纤维蛋白原(mg/dl)"                       DECIMAL(5, 1),
#     "入院第7天D二聚体(ng/ml)"                        DECIMAL(7, 1),
#     "入院第7天肌钙蛋白（TNI）（ng/ml）"                   DECIMAL(20, 18),
#     "入院第7天B型脑钠肽（BNP）（pg/ml）"                  DECIMAL(6, 1),
#     "入院第7天C-反应蛋白（mg/L）"                       DECIMAL(4, 1),
#     "入院第7天降钙素原（ng/ml）"                        DECIMAL(3, 1),
#     入院第7天酸碱度                                  DECIMAL(5, 3),
#     入院第7天氧分压                                  DECIMAL(5, 1),
#     入院第7天氧浓度                                  DECIMAL(4, 1),
#     入院第7天氧和指数                                 DECIMAL(18, 14),
#     入院第7天二氧化碳分压                               DECIMAL(4, 1),
#     入院第7天乳酸                                   DECIMAL(3, 1),
#     入院第7天碱剩余                                  DECIMAL(4, 1),
#     ISS                                       INTEGER,
#     AIS                                       INTEGER,
#     APACHEII                                  INTEGER,
#     股骨粗隆间骨折                                   INTEGER,
#     股骨颈骨折                                     INTEGER,
#     肋骨骨折                                      INTEGER,
#     骨盆骨折                                      INTEGER,
#     重度颅脑损伤                                    INTEGER,
#     血气胸                                       INTEGER,
#     股骨骨折                                      INTEGER,
#     股骨干骨折                                     INTEGER,
#     股骨骨折闭合复位髓内针内固定术                           INTEGER,
#     人工股骨头置换术                                  INTEGER,
#     股骨骨折切开复位髓内针内固定术                           INTEGER,
#     脑内血肿清除术                                   INTEGER,
#     创口负压引流术                                   INTEGER,
#     全髋关节置换术                                   INTEGER,
#     血管活性药物去甲肾上腺素                              INTEGER,
#     血管活性药物肾上腺素                                INTEGER,
#     血管活性药物多巴胺                                 INTEGER,
#     血管活性药物异丙肾                                 INTEGER,
#     肺部感染                                      INTEGER,
#     泌尿系感染                                     INTEGER,
#     菌血症                                       INTEGER,
#     急性弥漫性腹膜炎                                  INTEGER,
#     血流感染                                      INTEGER,
#     腹腔感染                                      INTEGER,
#     肠道感染                                      INTEGER,
#     肺炎                                        INTEGER,
#     出院转归类别                                    INTEGER,
#     手术部位                                      INTEGER
# )
#     organize by row;

