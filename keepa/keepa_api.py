import datetime
import numpy as np
import pandas as pd
import time
from dateutil.parser import parse
import keepa

ACCESSKEY = '7sommorss711l4ci5f3n97ftgvcq8jm7tak3316h3a61jkifqq3qh3keebkm9rsl'
k_api = keepa.Keepa(ACCESSKEY)


def get_info(items):
    check_basic = ['asin', 'title', 'imagesCSV', 'categories','categoryTree', 'brand', 'color', 'size', 'packageLength', 'itemWidth',
                   'itemHeight', 'itemWeight', 'packageLength', 'packageWidth', 'packageHeight', 'packageWeight', 'frequentlyBoughtTogether']

    check_date = ['NEW_time', 'NEW','SALES_time', 'SALES']

    info_list = []

    for each in k_api.query(items, domain='US'):
        info_each = {}
        for item in check_basic:
            info_each[item] = each.get(item, None)
        for date_item in check_date:
            info_each[date_item] = each.get('data', {}).get(date_item, np.array([]))
        info_list.append(info_each)
        print("已经获取的数据:", len(info_list))

    aft = datetime.datetime.now().strftime("%m%d%H%M") + '.xlsx'

    data = pd.DataFrame(info_list)
    print("数据转换中...")
    amazon_pic_domain = 'https://images-na.ssl-images-amazon.com/images/I/'
    amazon_pic_size = '_AC_UL320_SR360,360_.jpg' # 图片大小为360 实物占据320 其余留白
    # 主图获取
    data['pic_url_main'] = data['imagesCSV'].apply(lambda x : amazon_pic_domain + x.split(',')[0] + amazon_pic_size if x else None)
    # 确定图片数量
    data['pic_num'] = data['imagesCSV'].apply(lambda x: len(x.split(',')) if x else None)
    # 转化为excel可用的格式
    data['table_pic'] = '<table> <img src=' + '\"' + data['pic_url_main'] + '\"' + 'height="140" >'
    print(data['table_pic'])
    # 第一次销售时间
    data['data_on_sale'] = data['SALES_time'].apply(lambda x: x[0])
    print(data['data_on_sale'])
    # 当前价格
    data['price_now'] = data['NEW'].apply(lambda x: x[-1] if x.any() else None)
    print(data['price_now'])

    data['max_rank'] = data['SALES'].apply(lambda x: x.max() if x.any() else None)
    print(data['max_rank'])

    # data['min_rank'] = data['SALES'].apply(lambda x: x.min() if )

    # data['max_time'] = data[data['SALES'] == data['max_rank']]['SALES_time']

    # data['pre_rank'] = np.mean(data['SALES'])

    data.to_excel('asin_info_' + aft, encoding='utf-8', engine='xlsxwriter')
    print('转换完成, 存储至excel')
    return data


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
        rank_in=8000,
        rank_out=15000,
        review_count=60,
        date_in='2019-1-1',
        date_out='2019-9-15',
        category=cate_info['Patio, Lawn & Garden']):  # category查上述字典

    query_json = {
        "current_SALES_gte": rank_in,  # 最高排名
        "current_SALES_lte": rank_out,  # 最底排名
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
        "productType": [0, 1, 5],
        "perPage": 2000,  # 每一页展示的数据
        "page": 0  # 第几页
    }

    return query_json


def get_cate(row_cat=0):

    cate_info = k_api.category_lookup(row_cat)
    pd.DataFrame(cate_info).T.to_excel('categories_'+str(row_cat)+'.xlsx', encoding='utf-8')


if __name__ == '__main__':

    # 从文件获取ASIN
    # file_path = r'asin_lsit_10251719.xlsx'
    # items = pd.read_excel(file_path)['asin'].tolist()
    # aft = datetime.datetime.now().strftime("%m%d%H%M") + '.xlsx'
    # pd.DataFrame(items, columns=['ASIN']).to_excel(aft, encoding='utf-8', engine='xlsxwriter')

    # 从keepa请求获取asin
    items = k_api.product_finder(get_selection(category=cate_info['Sports & Outdoors']))

    get_info(items=items)

