from aip import AipNlp
import json
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

# https://blog.csdn.net/cyinfi/article/details/88046887

class baidu_nlp_ts(object):
    """对百度的自然语言api进行使用和测试"""
    def __init__(self):
        """ 你的 APPID AK SK """
        APP_ID = '24071765'
        API_KEY = 'WjhpRvhqw3WzdoBs7lymvXhX'
        SECRET_KEY = 'D2bu0beOywUY3kabby3E3f3kS6CqK0za'

        self.client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

    def lexer(self, text):
        """"""
        # text = "百度是一家高科技公司"

        """ 调用词法分析 """
        res = self.client.lexer(text);
        print(res)
        return res


    def tst_pingtai(self):
        """"""
        text = "百度是一家高科技公司"

        """ 调用词法分析 """
        res = self.client.lexer(text);
        print(res)

        """ 调用依存句法分析 """
        res = self.client.depParser(text);
        print(res)

        word = "张飞"

        """ 调用词向量表示 """
        res = self.client.wordEmbedding(word);
        print(res)

        text = "床前明月光"

        """ 调用DNN语言模型 """
        res = self.client.dnnlm(text);
        print(res)

        word1 = "海洋"
        word2 = "天空"
        word3 = "海"

        """ 调用词义相似度 """
        res = self.client.wordSimEmbedding(word1, word2);
        res1 = self.client.wordSimEmbedding(word1, word3);
        print(res)
        print(res1)

        text1 = "浙富股份"

        text2 = "万事通自考网"

        """ 调用短文本相似度 """
        res = self.client.simnet(text1, text2);

        """ 如果有可选参数 """
        options = {}
        options["model"] = "CNN"

        """ 带参数调用短文本相似度 """
        self.client.simnet(text1, text2, options)

        text = "三星电脑电池不给力"

        """ 调用评论观点抽取 """
        res = self.client.commentTag(text);

        """ 如果有可选参数 """
        options = {}
        options["type"] = 13

        """ 带参数调用评论观点抽取 """
        res = self.client.commentTag(text, options)

        text = "苹果是一家伟大的公司"

        """ 调用情感倾向分析 """
        res = self.client.sentimentClassify(text);

        title = "iphone手机出现“白苹果”原因及解决办法，用苹果手机的可以看下"

        content = "如果下面的方法还是没有解决你的问题建议来我们门店看下成都市锦江区红星路三段99号银石广场24层01室。"

        """ 调用文章标签 """
        self.client.keyword(title, content);

if __name__ == "__main__":
    b = baidu_nlp_ts()
    res = b.lexer('患者10个月前发现右侧阴囊较左侧大，无明显疼痛，当地医院完善彩超提示右侧睾丸增大伴血流信号增多，右侧精索静脉曲张，口服抗生素（法罗培南）1周无明显好转。2018-7-17就诊于北京大学第一医院，行核磁检查示右侧睾丸体积增大，T2W1信号轻度均匀减低，结构清楚，增强扫描未见异常强化，DWI呈稍高信号，继续口服抗生素及中药治疗。2019-1-18复查彩超示右侧睾丸明显增大，体积8.2*4.9*6.1cm，包膜尚光滑，回声不均匀，可见丰富血流信号，右侧附睾头3.91cm，右侧附睾尾直径2.43cm，右附睾增大，可见丰富血流信号。2019-2-20全麻下行右侧睾丸根治性切除术，北医三院病理会诊，偶见曲细精管残留。大部分区域见异型细胞弥漫增生，并有大片状凝固性坏死。肿瘤细胞形态单一，体积中等偏大，胞浆丰富、淡染，核大、略不规则，染色质稀疏，核分裂像易见。免疫组化：CD3（+），CD56（+），TIA-1（+），Ki67（85%+），CD34（-），CD8（-），Pax5（-），MPO（-），GramB（-），诊断睾丸NK/T细胞淋巴瘤。3周前出现右上肢麻木，伴后伸运动障碍，伴局部麻木感。2019-4-17完善PET-CT示：右侧臂丛神经、右肺多发磨玻璃密度影及右侧髂前上棘邻近皮肤FDG代谢增高考虑淋巴瘤累及可能性大；右侧睾丸术后，局部术后改变；右侧上颌窦炎；左侧肾上腺结节考虑腺瘤可能性大。近1周有咳嗽，偶有咳痰，无发热。病程中患者精神、食欲、睡眠尚可，大小便正常，体力、体重较前无著变。')
    lexerDf = pd.DataFrame(res['items'])
    lexerDf['item']


