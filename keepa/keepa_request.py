import requests
import pandas as pd
import time, datetime
from dateutil.parser import parse
import urllib
import json
from jsonpath import jsonpath

KEEPA_KEY = '7sommorss711l4ci5f3n97ftgvcq8jm7tak3316h3a61jkifqq3qh3keebkm9rsl'  # keepa密钥
domain = '1'  # 亚马逊的市场 美国为1

def get_keepa_time(date):
    """
    把普通的时间格式转化为keep时间格式
    :param date:
    :return:
    """
    return int(time.mktime(parse(date).timetuple())/60-21564000)


cate_info = {
    "Apps & Games": 2350149011,
    "Baby Products": 165796011,
    "Digital Music": 163856011,
    "Toys & Games": 165793011,
    "Patio, Lawn & Garden": 2972638011,
    "Books": 283155,
    "Arts, Crafts & Sewing": 2617941011,
    "Software": 229534,
    "Sports & Outdoors": 3375251,
    "Handmade Products": 11260432011,
    "Video Games": 468642,
    "Clothing, Shoes & Jewelry": 7141123011,
    "Office Products": 1064954,
    "Grocery & Gourmet Food": 16310101,
    "Tools & Home Improvement": 228013,
    "Movies & TV": 2625373011,
    "Musical Instruments": 11091801,
    "Appliances": 2619525011,
    "Collectibles & Fine Art": 4991425011,
    "Pet Supplies": 2619533011,
    "Industrial & Scientific": 16310091,
    "Cell Phones & Accessories": 2335752011,
    "Everything Else": 10272111,
    "Home & Kitchen": 1055398,
    "Beauty & Personal Care": 3760911,
    "CDs & Vinyl": 5174,
    "Electronics": 172282,
    "Automotive": 15684181,
    "Health & Household": 3760901,
    "Vehicles": 10677469011,
}


def get_selection(
        category=1055398,
        rank_in=3000,
        rank_out=30000,
        review_count=60,
        date_in='2019-1-1',
        date_out='2019-9-15',
    ):
    queryJson = {
         "current_SALES_gte": rank_in,  # 最高排名
         "current_SALES_lte":  rank_out,  # 最底排名
         "current_COUNT_REVIEWS_gte": 0,  # 最低评价数量
         "current_COUNT_REVIEWS_lte": review_count,  # 最高评价数量
         "current_NEW_FBA_gte": 2000,  # FBA发货价格 最低20刀
         "current_NEW_FBA_lte": 5000,
         "avg30_NEW_FBA_gte": 2000,  # 30天平均最低发货价格20刀
         "avg30_NEW_FBA_lte": 5000,
         "trackingSince_gte": get_keepa_time(date_in),  # 跟踪时间不早于
         "trackingSince_lte": get_keepa_time(date_out),  # 跟踪时间不晚于
         "rootCategory": category,  # 跟类目节点
         "packageLength_gte": 1,
         "packageLength_lte": 450,
         "packageWidth_gte": 1,
         "packageWidth_lte": 450,
         "packageHeight_gte": 1,
         "packageHeight_lte": 450,  # 打包最大边长不高于450mm
         "packageWeight_gte": 1,
         "packageWeight_lte": 1800,  # 打包重量不高于1800g
         "sort": [["current_SALES", "asc"]],
         "lastOffersUpdate_gte": 4631500,  # int(time.time()/60-21564000)
         "lastRatingUpdate_gte": 4615660,
         "productType": [0, 1, 5],   # 0 所有产品， 1
         "perPage": 3000,  # 每一页展示的数据
         "page": 0  # 第几页
    }
    return queryJson


def get_asin():
    cate_key = 'Home & Kitchen'
    rank_in = 3000
    rank_out = 30000

    url = "https://api.keepa.com/query?key=" + KEEPA_KEY + "&domain=" + domain + '&selection=' + \
          urllib.parse.quote(json.dumps(get_selection(category=cate_info[cate_key],
                                                      rank_in=rank_in,
                                                      rank_out=rank_out)))
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/77.0.3865.120 Safari/537.36'
    })
    print(url)
    rep_data = s.get(url, verify=False)
    print(rep_data.text)
    file_name = "asin_list_" + datetime.datetime.now().strftime('%m%d%H%M') + '_' + cate_key + '_' + \
                str(rank_in) + '_' + str(rank_out) + '.csv'
    data_pd = pd.DataFrame(rep_data.json()['asinList'], columns=['ASIN'])
    data_pd.to_csv(file_name, encoding='utf-8')

    return data_pd


def get_varies(ASIN):
    asin_json = asin_info(ASIN)

    variationCSV = jsonpath(asin_json, '$.products[0].variationCSV')
    if variationCSV[0]:
        return variationCSV
    else:
        parent_asin = jsonpath(asin_json, '$.products[0].parentAsin')[0]
        print(parent_asin)
        parent_info = asin_info(parent_asin)
        return jsonpath(parent_info, '$.products[0].variationCSV')

def asin_info(ASIN):
    s = requests.Session()
    url = "https://api.keepa.com/product?key=" + KEEPA_KEY + "&domain=" + domain + "&update=-1" + "&asin=" + ASIN
    print(url)
    res_json = s.get(url).json()
    if res_json.get('products'):
        # print(res_json)
        return res_json
    else:
        return None


if __name__ == '__main__':

    asin_list = ['B07QQ9WR8L']
    for each in asin_list:
        print(get_varies(each))
