# 日本站商品详情

import numpy as np
import pandas as pd
import requests, lxml
from lxml import etree
import re, time, random, datetime


def weight_handle(weight):
    # 把kg g 都转化为数字存储
    if re.search("kg", weight.lower()):
        weight_int = float(weight.split(' ')[0]) * 1000
    else:
        weight_int = float(weight.split(' ')[0])

    return weight_int


def feature_handle(feature):
    import re
    patt = re.compile('(\d+)[^\d+]*[by\*x]\s*(\d+)')
    res = re.search(patt, feature.lower()).groups()
    return res

class GoodDetail:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }

    proxies = {
        "http": "http://114.239.3.156:9999",
    }

    url_base = "https://www.amazon.co.jp"
    s = requests.Session()
    s.get(url=url_base, headers=headers)

    def __init__(self):
        self.detail_list = []

    def get_detail(self, url):
        import re
        if re.search('slredirect', url):
            is_ad = 1
        else:
            is_ad = 0
        res = self.s.get(url, headers=self.headers)
        if str(res.status_code) != '200':
            print("请求出错，状态码为：%s" % res.status_code)
            print(res.text)
            return

        from bs4 import BeautifulSoup
        soup_res = BeautifulSoup(res.text, features="lxml")
        detail_text = soup_res.select('body')
        res_html = etree.HTML(str(detail_text[0]))

        # 标题
        try:
            title = res_html.xpath("string(//span[@id='productTitle'])")
            title = title.replace("\n",'').replace('\t', '').strip()
        except:
            title = None

        # 品牌
        try:
            brand = res_html.xpath("string(//a[@id='bylineInfo'])")
            print(brand)
        except:
            brand = None
        # 图片链接
        try:
            goods_pic_url = res_html.xpath('//img[@id="landingImage"]/@src')[0]
        except:
            goods_pic_url = None

        # 价格
        try:
            price = res_html.xpath('//span[@id="priceblock_ourprice"]/text()')[0]

        except:
            price = None

        if not price:
            try:
                price = res_html.xpath('//span[@id="priceblock_pospromoprice"]/text()')[0]
            except:
                price = None
        if not price:
            try:
                price = res_html.xpath('//span[@id="priceblock_dealprice"]/text()')[0]
            except:
                price = None
        # 评价数量
        try:
            review_counts = res_html.xpath('//span[@id="acrCustomerReviewText"]/text()')[0]
            review_counts = int(review_counts.split("件")[0].replace(",", ""))
        except:
            review_counts = None

        # 评价星级
        try:
            review_starts = res_html.xpath('//div[@id="averageCustomerReviews"]//span[@class="a-icon-alt"]/text()')[0]
            review_starts = float(review_starts.split(" ")[-1])
        except:
            review_starts = None

        # 变体ASIN
        try:
            sort_ASIN = res_html.xpath("//div[@id='variation_color_name']//li/@data-defaultasin")
        except:
            sort_ASIN = None

        # 商品详情信息
        item = {}
        # if res_html.xpath('//table[@id="productDetailsTable"]//div[@class="content"]/ul/li'):
        #     print("model-li")
        #     for each in res_html.xpath('//table[@id="productDetailsTable"]//div[@class="content"]/ul/li'):
        #         li = each.xpath('string(.)')
        #         li = li.replace('\n', '').replace('\t', '')
        #         # print(li)
        #         if re.search(":", li):
        #             key = li.split(":")[0].strip()
        #             value = li.split(":")[1].strip()
        #             if not (re.search('rank', key.lower()) or re.search('review', key.lower())):
        #                 item[key] = value
        #             print(key, value)
        #         if re.search("：", li):
        #             key = li.split("：")[0].strip()
        #             value = li.split("：")[1].strip()
        #             print(key, value)
        #             if not (re.search('rank', key.lower()) or re.search('review', key.lower())):
        #                 item[key] = value
        #
        #
        #     goods_ranks = res_html.xpath('string(//li[@id="SalesRank"])')
        #     item['goods_ranks'] = goods_ranks

        # if res_html.xpath('//div[@id="detail-bullets_feature_div"]//div[@class="content"]/ul/li'):
        #     print("model-li")
        #     for each in res_html.xpath('//div[@id="detail-bullets_feature_div"]//div[@class="content"]/ul/li'):
        #         li = each.xpath('string(.)')
        #         li = li.replace('\n', '').replace('\t', '')
        #         if re.search(":", li):
        #             key = li.split(":")[0].strip()
        #             value = li.split(":")[1].strip()
        #             if not (re.search('rank', key.lower()) or re.search('review', key.lower())):
        #                 item[key] = value
        #             print(key, value)
        #         if re.search("：", li):
        #             key = li.split("：")[0].strip()
        #             value = li.split("：")[1].strip()
        #             print(key, value)
        #             if not (re.search('rank', key.lower()) or re.search('review', key.lower())):
        #                 item[key] = value
        #
        #     goods_ranks = res_html.xpath('string(//li[@id="SalesRank"])')
        #     item['goods_ranks'] = goods_ranks

        if res_html.xpath('//div[@id="detail_bullets_id"]//div[@class="content"]/ul/li'):
            print("model-li")
            for each in res_html.xpath('//div[@id="detail_bullets_id"]//div[@class="content"]/ul/li'):
                li = each.xpath('string(.)')
                li = li.replace('\n', '').replace('\t', '')
                if re.search(":", li):
                    key = li.split(":")[0].strip()
                    value = li.split(":")[1].strip()
                    item[key] = value
                if re.search("：", li):
                    key = li.split("：")[0].strip()
                    value = li.split("：")[1].strip()
                    item[key] = value
                    print(key, value)

            goods_ranks = res_html.xpath('string(//li[@id="SalesRank"])')
            item['Amazon 売れ筋ランキング'] = goods_ranks

        if res_html.xpath("//div[@class='wrapper JPlocale']"):
            print("model-tr")
            for each in res_html.xpath("//div[@class='wrapper JPlocale']//tr"):
                key = each.xpath("string(.//td[@class='label'])")
                value = each.xpath("string(.//td[@class='value'])")
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    item[key] = value

        # 商品详情拆分
        ASIN = item.get('ASIN', None)
        product_dimensions = item.get('商品パッケージの寸法', None)
        package_dimensions = item.get('梱包サイズ', None)
        product_weight = item.get('商品重量', None)
        ship_weight = item.get('発送重量', None)
        since_date = item.get('Amazon.co.jp での取り扱い開始日', None)
        goods_ranks = item.get('Amazon 売れ筋ランキング', None)

        if goods_ranks:
            print("---")
            import re
            goods_rank = goods_ranks.replace("\n", '').replace("\t", '').replace("\xa0", ' ')
            patt = re.compile(r'[\(\{].*[\)\}]')
            patt2 = re.compile(r'\s{2,}')
            goods_rank = re.sub(patt, '', goods_rank)
            goods_rank = re.sub(patt2, ' ', goods_rank)
            goods_ranks = goods_rank.split(':')[-1]
            print('goods_rank_raw:', goods_ranks)

            # for each in goods_rank.split('#')[1:]:
            #     goods_rank_num, goods_rank_sort = each.split("in", 1)
            #     weight_str = re.compile(r'\(.*\)')
            #     goods_rank_sort = re.sub(weight_str, '', goods_rank_sort)
            #     goods_each_ranks.append((goods_rank_num.strip(), goods_rank_sort.strip()))
            #     print(goods_each_ranks)

        each_detail_list = (title, goods_pic_url, ASIN, brand, is_ad, price, review_counts, review_starts, goods_ranks,
                            product_dimensions, package_dimensions, product_weight, ship_weight, since_date, sort_ASIN)

        self.detail_list.append(each_detail_list)



def pic_save(base_code, ASIN):

        import base64
        img_data = base64.b64decode(base_code)
        file = open(r"E:\爬虫pycharm\data\pic\\" + str(ASIN)+'.jpg', 'wb')
        file.write(img_data)
        file.close()

if __name__ == '__main__':

    # data_file = r'E:\爬虫pycharm\data\goods_rank_list\珪藻土 バスマット-07030931_with_ad.csv'
    # data = pd.read_csv(data_file)
    data_file = r'E:\产品开发\prime day 数据\终版\日本多类目数据.xlsx'
    row_data= pd.read_excel(data_file)

    data = pd.DataFrame(row_data)
    data.drop_duplicates(subset=['asin'], inplace=True)
    print(data)
    goods_detail = GoodDetail()
    # for url in data['goods_url_full']:
    #     if url:
    #         print(url)
    #         goods_detail.get_detail(url)
    #         time.sleep(random.randint(2,5))

    for asin in data['asin']:
        if asin:
            url = "https://www.amazon.co.jp/dp/" + asin
            print(url)
            # file_pic = r'E:\爬虫pycharm\data\pic\\' + asin + '.jpg'
            goods_detail.get_detail(url)
            time.sleep(random.uniform(1.5,2.3))

    details_pd = pd.DataFrame(goods_detail.detail_list,
                              columns=['title','goods_pic_url', 'ASIN', 'brand','is_ad', 'price', 'review_counts',
                                       'review_starts', 'goods_ranks','product_dimensions', 'package_dimensions',
                                       'product_weight','ship_weight', 'since_date', 'sort_ASIN'])

    aft = datetime.datetime.now().strftime('%m%d%H%M')

    for base_code_full, ASIN in zip(details_pd['goods_pic_url'], details_pd['ASIN']):
        try:
            if base_code_full and ASIN:
                base_code = base_code_full.split(',')[1]
                pic_save(base_code, ASIN)
        except:
            pass

    time.sleep(3)
    details_pd['pic_url'] = "E:\爬虫pycharm\data\pic\\" +  details_pd['ASIN'] + ".jpg"
    details_pd['pic_table_url'] = '<table> <img src=' + '\"' +details_pd['pic_url'] + '\"' +'height="150" >'
    file_name_new = "E:\爬虫pycharm\data\goods_detail\\" + aft + "_with_ad.xlsx"
    details_pd.to_excel(file_name_new,  encoding='utf-8')