# 对评论详情进行词频分布统计
import numpy as np
import pandas as pd
import pyecharts
from pyecharts import WordCloud
import datetime, time
from .words_filter import word_filter


def words_handle(text, *args):
    return text

def get_counts(text, *args):
    # 输入文字段 先进行替换 然后 分词
    words_filter = word_filter + ['shelves']
    import re
    txt = text.lower()
    step = re.compile(r'[\"~!@#$%^&*()_+{}|\[\]:;<>?.,，]')  # 替换特殊字符
    txt = re.sub(step,' ', txt)
    words_row = txt.split()  # 分词
    counts = {}
    for word in words_row:
        if word not in words_filter:
            counts[word] = counts.get(word, 0)+1

    items = list(counts.items())  # 输出words value 的字典
    items.sort(key=lambda x: x[1], reverse=True)  # 把字典按照数值排序
    return items


def get_pic(items, m, n):

    # 输入item, 选择显示分布排列为 m-n 的关键词
    text_rank = pd.DataFrame(items, columns=['words', 'value'])

    from pyecharts import WordCloud
    name = text_rank['words'][m:n+1]
    value = text_rank['value'][m:n+1]
    word_cloud = WordCloud(width=1300, height=620)
    word_cloud.add("", name, value, word_size_range=[20, 100], shape='diamond',)
    aft = datetime.datetime.now().strftime('%m%d%H%M')
    word_cloud.render(r"E:\爬虫pycharm\data\goods_review\reword_cloud" + aft + ".html")

if __name__ == '__main__':
    # data_path = r'E:\模拟开发\美国站\bath pillow\\'
    f = '..\data\goods_review\diaper bag_评论TOP50.xlsx'
    data = pd.read_excel(f)
    # data.columns=['#', 'view_goods', 'view_name', 'view_star', 'view_title', 'view_date', 'view_colour', 'view_size', 'view_body', 'view_useful']
    # print(data['review_body'])
    data_filter = data['review_body'][data['review_body'].notnull()][data['review_star'] <= 3]
    text = " ".join(data_filter)
    items = get_counts(text)
    aft = datetime.datetime.now().strftime('%m%d%H%M')
    pd.DataFrame(items).to_csv(r"../data/goods_review/词频分布"+ aft + '.csv')
    print(items)
    get_pic(items, 0, 100)
    words = list(m for m, n in items[:5])
    time.sleep(3)
    while True:
    # 列出包含最高频的几个词语的评论
        word_list = (input("请输入要查询的词语，以逗号隔开，退出请输入quit:",))
        if word_list == ('quit'):
            break
        res_list = list(i.strip() for i in word_list.split(',') if i)

        for word in res_list:
            num = 1
            for each in data_filter:
                if word in str(each):
                    print("{:*^20}".format(word + ":" + str(num)))
                    print(each.replace(word, '\033[1;31;40m'+ word +'\033[0m'))
                    num += 1


