# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 17:18:15 2020

@author: 西湖味精三月鲜
"""

# 百度获取日历
# https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query=2020%E5%B9%B4&resource_id=6018&format=json


import pandas as pd
import requests
import json
import numpy as np


# 生成某一年的日历
def gen_calendar(year=2020):
    # 生成日历列表
    start_date = str(year) + '0101'
    end_date = str(year) + '1231'
    df = pd.DataFrame()
    dt = pd.date_range(start_date, end_date, freq='1D')
    df['date'] = dt
    # 计算周几
    df['dayofweek'] = df['date'].dt.dayofweek + 1
    # 获取法定节假日
    up1 = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query='
    up2 = '%E5%B9%B4&resource_id=6018&format=json'
    url = "".join([up1, str(year), up2])
    r = requests.get(url)
    r_json = json.loads(r.text)
    # 获取放假信息
    h_data = r_json['data'][0]['holiday']
    h_df = pd.DataFrame()
    for i in range(len(h_data)):
        each_d = h_data[i]['list']
        each_df = pd.DataFrame(each_d)
        h_df = h_df.append(each_df)
    # 处理一下数据，去重等等
    h_df.drop_duplicates(inplace=True)
    h_df.reset_index(drop=True, inplace=True)
    h_df['date'] = pd.to_datetime(h_df['date'])

    # 合并数据
    df2 = pd.merge(df, h_df, how='left', on='date')
    df2.fillna(0, inplace=True)
    df2['status'] = df2['status'].astype('int')
    # 返回是否假日
    judge = np.where(df2['dayofweek'] < 6, 0, 1) + df2['status']
    judge = np.where((judge == 2) | (judge == 1), 'Y', 'N')
    df2['isholiday'] = judge

    return df2

# 生成某一年的日历
def get_all_calendar():
    allDf = []
    for year in range(2014, 2020):
        df = gen_calendar(year)
        if len(allDf) == 0:
            allDf = df
        else:
            allDf = pd.concat([allDf, df], axis=0)

    return allDf

if __name__ == '__main__':
    year = 2014
    df = gen_calendar(year)
