import numpy as np
import pandas as pd
import requests, lxml
from lxml import etree
import re, time, random, datetime
import pymysql
import os

def weight_handle(weight):
    # 把kg ounce pound 都转化为数字存储
    weight = weight.lower().replace(',', '')
    if re.search("kg", weight):
        weight_int = float(weight.split(' ')[0]) * 1000

    elif re.search("ounce", weight):
        weight_int = float(weight.split(' ')[0]) * 28.35

    elif re.search("pound", weight):
        weight_int = float(weight.split(' ')[0]) * 453.60

    else:
        try:
            weight_int = float(weight.split(' ')[0])
        except:
            weight_int = weight
    return weight_int


def feature_handle(feature):
    import re
    patt = re.compile('(\d+)[^\d+]*[by\*x]\s*(\d+)')
    res = re.search(patt, feature.lower()).groups()
    return res


def seller_handle(seller):
    # 卖家类型识别
    if not seller:
        return None
    else:
        if re.search('sold by Amazon.com', seller, re.I):
            return 'AMZ'
        elif re.search('Fulfilled by Amazon', seller, re.I):
            return 'FBA'
        else:
            return 'FBM'

def get_sales(rank, cate="Home & Kitchen"):
    import requests
    import urllib

    s = requests.Session()
    proxies = {
        "http": "http://180.118.247.88:9000"
    }
    row_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    }
    raw_url = "https://amzscout.net/"
    s.get(raw_url, headers=row_headers, proxies=proxies)

    # 销量预测接口，返回根据类目排名得到的销量预测，仅供参考
    test_header ={
        "Host": "amzscout.net",
        "Connection": "keep-alive",
        "Content-Length": "49",
        "Origin": "https://amzscout.net",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Referer": "https://amzscout.net/sales-estimator/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    test_url = "https://amzscout.net/analytics/v1/events"
    data = 'category=Estimator&action=search&software=LANDING'
    s.post(url=test_url, headers=test_header, data=data, proxies=proxies)

    url = "https://amzscout.net/estimator/v1/sales?domain=COM&category=" + urllib.parse.quote(cate)+ "&rank=" + str(rank)
    ams_headers = {
        "Host": "amzscout.net",
        "Connection":"keep-alive",
        "Cache-Control":"max-age=0",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9",
    }
    try:
        res = s.get(url, headers=ams_headers)
        return res.json().get('sales')
    except:
        return None


class GoodDetail:
    headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
    }

    proxies = {
        "http": "http://114.217.241.20:8118",
    }

    url_base = "https://www.amazon.com"

    conn = pymysql.connect(host='localhost', port=3306, db='amazon_test', user='root', passwd='1118')
    s = requests.Session()
    s.get(url=url_base, headers=headers, verify=False)

    def __init__(self):
        self.detail_list = []
        self.rank_list = []
        self.sec_list = []
        self.begin = 0

    def get_detail(self, url):
        import re
        if re.search('slredirect', url):
            ad_plus = 1
        else:
            ad_plus = 0
        res = self.s.get(url, headers=self.headers, verify=False)
        if str(res.status_code) != '200':
            print("页面错误，状态码为：", res.status_code)
            print(res.text)
            return

        from bs4 import BeautifulSoup
        soup_res = BeautifulSoup(res.text, features='lxml')
        detail_text = soup_res.select('body')
        res_html = etree.HTML(str(detail_text[0]))

        try:
            goods_title = res_html.xpath("string(//span[@id='productTitle'])")
            goods_title = goods_title.replace("\n",'').replace('\t', '').strip()
        except:
            goods_title = None

        if not goods_title:
            time.sleep(random.uniform(2,5))
            print("try again")
            self.begin += 1
            if self.begin >= 5:
                print('该链接:' + url + '访问出错次数超过5次,可能该链接下没有同类商品内容')
                return
            self.get_detail(url)

        print(self.begin)
        self.begin = 0
        # 类别
        kinds = res_html.xpath("//div[@class='twisterTextDiv text']/span[@class='a-size-base' and 1]/text()")[:]

        # sort_list = []
        if not kinds:
            kinds = res_html.xpath('//div[@class="a-section a-spacing-none twisterShelf_displaySection"]/span/text()')[:]

        # 不同类别、颜色、款式的编号
        # sorts_codes = res_html.xpath('//*[starts-with(@id, "size_name")]/@data-defaultasin')[:]
        # color_sorts = res_html.xpath('//*[starts-with(@id, "color_name")]/@data-defaultasin')[:]
        # style_sorts = res_html.xpath('//*[starts-with(@id, "style_name")]/@data-defaultasin')[:]
        # sort_list = sorts_codes + color_sorts + style_sorts

        try:
            sorts_codes = res_html.xpath('//*[starts-with(@id, "size_name")]/@data-dp-url')[:]
            color_sorts = res_html.xpath('//*[starts-with(@id, "color_name")]/@data-dp-url')[:]
            style_sorts = res_html.xpath('//*[starts-with(@id, "style_name")]/@data-dp-url')[:]

            sort_list_raw = sorts_codes + color_sorts + style_sorts
            asin_patt = re.compile("dp/(.*)/")

            sort_list = [re.search(asin_patt, each).groups()[0] for each in sort_list_raw if each]
            sort_list = list(set(sort_list))
        except:
            sort_list = []

        try:
            choosen_kinds = res_html.xpath('//div[starts-with(@id, "variation")]/div/span/text()')
            if choosen_kinds:
                choose_kind = choosen_kinds[0].strip()
            else:
                choose_kind = res_html.xpath('//span[@class="shelf-label-variant-name"]/text()')[0].strip()
        except:
            choose_kind = "Just One Kind"

        item = {}
        if res_html.xpath('//div[@id="detail-bullets"]//div[@class="content"]/ul/li'):
            print("model-0")
            for each in res_html.xpath('//div[@id="detail-bullets"]//div[@class="content"]/ul/li'):
                li = each.xpath('string(.)')
                li = li.replace('\n', '').replace('\t', '')
                try:
                    key = li.split(":")[0].strip()
                    value = li.split(":")[1].strip()
                except:
                    key = 'miss key'
                    value = 'miss value'
                import re
                if not (re.search('rank', key.lower()) or re.search('review', key.lower())):
                    item[key] = value
            goods_rank = res_html.xpath('string(//li[@id="SalesRank"])')
            item['raw_goods_rank'] = goods_rank

        if res_html.xpath("//div[@id='detailBullets_feature_div']/ul"):
            absr = res_html.xpath('string(//div[@id="dpx-amazon-sales-rank_feature_div"]/li)')
            item['Amazon Best Sellers Rank'] = absr
            print("model-1")
            for each in res_html.xpath('//div[@id="detailBullets_feature_div"]/ul/li'):
                key = each.xpath('.//span/span[1]/text()')
                # print(key)
                value = each.xpath('.//span/span[2]/text()')
                # print(value)
                if key and value:
                    key = key[0].replace("\n", '').replace("\t", '').strip(": (")
                    value = value[0].replace("\n", '').replace("\t", '').strip(": (")
                    print(key, "---", value)
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//div[@class='a-section table-padding']/table//tr"):
            print("model-2")
            for each in res_html.xpath("//div[@class='a-section table-padding']/table//tr"):
                key = each.xpath("string(.//th)")
                # print(key, "---")
                value = each.xpath("string(.//td)")
                #     print(key, value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//table[@id='productDetails_detailBullets_sections1']"):
            print("model-3")
            for each in res_html.xpath("//table[@id='productDetails_detailBullets_sections1']//tr"):
                # print("model1--in")
                key = each.xpath("string(./th)")
                # print(key, "---")
                value = each.xpath("string(./td)")
                # print(key, value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value


        if res_html.xpath("//table[@id='productDetails_techSpec_section_1']"):
            print("model-4")
            for each in res_html.xpath("//table[@id='productDetails_techSpec_section_1']//tr"):
                key = each.xpath("string(.//th)")
                # print(key, "---")
                value = each.xpath("string(.//td)")
                # print(key, value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//div[@class='wrapper USlocale']"):
            print("model-5")
            for each in res_html.xpath("////div[@class='wrapper USlocale']//tr"):
                # print("model3--in")
                key = each.xpath("string(.//td[@class='label'])")
                # print(key, "---")
                value = each.xpath("string(.//td[@class='value'])")
                # print(key, "---", value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value
                        print(key,"---", value)

        # 图片路径
        try:
            goods_pic_url = res_html.xpath('//img[@id="landingImage"]/@src')[0]
        except:
            goods_pic_url = None

        ASIN = item.get('ASIN', None)

        try:
            multi_asin = set(sort_list.append(ASIN))
        except:
            multi_asin = set(sort_list)
        print("-----------")
        print(multi_asin)
        print("-----------")
        product_dimensions = item.get('Product Dimensions', None)
        package_dimensions = item.get('Package Dimensions', None)
        product_weight = item.get('Item Weight', None)
        date_on_shelf = item.get('Date first listed on Amazon', None)

        if product_weight:
            product_weight = weight_handle(product_weight)
        ship_weight = item.get('Shipping Weight', None)
        if ship_weight:
            ship_weight = weight_handle(ship_weight)


        feature_list = res_html.xpath("//div[@id='feature-bullets']/ul/li/span/text()")
        features = []
        for feature in feature_list:
            feature = feature.strip()
            features.append(feature)

        rank_in_HK = None
        goods_ranks = item.get('raw_goods_rank', None)
        goods_each_ranks = goods_ranks
        print(goods_ranks)
        if not goods_ranks:
            goods_ranks = item.get('Best Sellers Rank', None)
            if not goods_ranks:
                    goods_ranks = item.get('Amazon Best Sellers Rank', None)

        category_main = None
        rank_main = None
        if not goods_ranks:
            goods_each_ranks = {}
            self.rank_list.append(goods_each_ranks)

        if goods_ranks:
            print("---")
            import re
            weight_str = re.compile(r'\(.*\)')
            goods_rank = goods_ranks.replace("\n", '').replace("\t", '').replace("\xa0", ' ')
            patt = re.compile(r'[\(\{].*[\)\}]')
            patt2 = re.compile(r'\s{2,}')
            goods_rank = re.sub(patt, '', goods_rank)
            goods_rank = re.sub(patt2, ' ', goods_rank)
            goods_each_ranks = {}

            for each in goods_rank.split('#')[1:]:
                goods_rank_num, goods_rank_sort = each.split("in", 1)
                try:
                    goods_rank_num = int(goods_rank_num.replace(',','').strip())
                except:
                    pass
                goods_rank_sort = re.sub(weight_str, '', goods_rank_sort)
                goods_each_ranks[goods_rank_sort.strip()] = goods_rank_num
                if re.search('Home & Kitchen', goods_rank_sort):
                    try:
                        rank_in_HK = int(goods_rank_num)
                    except:
                        rank_in_HK = None

            self.rank_list.append(goods_each_ranks)
            print(self.rank_list[-1])


            try:
                category_main = list(self.rank_list[-1].keys())[0]
                rank_main = int(list(self.rank_list[-1].values())[0])
            except:
                category_main, rank_main = None, None
            print(category_main, rank_main)
        # 评价数量
        try:
            goods_review_count = res_html.xpath('//div[@id="averageCustomerReviews"]//span[@id="acrCustomerReviewText"]/text()')[0]
            goods_review_count = int(goods_review_count.split(" ")[0].replace(",", ""))
        except:
            goods_review_count = 0

        # 评价星级
        try:

            goods_review_star = res_html.xpath('//div[@id="averageCustomerReviews"]//span[@class="a-icon-alt"]/text()')[0]
            goods_review_star = float(goods_review_star.split(" ")[0])
        except:
            goods_review_star = None

        # 高频评价
        fre_words = res_html.xpath('//*[@id="cr-lighthut-1-"]/div/span/a/span/text()')[:]
        high_fre_words = [each.strip() for each in fre_words if each]

        try:
            goods_price = res_html.xpath("//span[starts-with(@id,'priceblock')]/text()")[0]
        except:
            goods_price =None

        import json
        try:
            brand = res_html.xpath('//a[@id="bylineInfo"]/text()')[0]
        except:
            brand = None
        try:
            buy_box_info =  res_html.xpath('//*[@id="turboState"]/script/text()')[0]
            buy_box_json = json.loads(buy_box_info)
            stockOnHand = buy_box_json['eligibility']['stockOnHand']
        except:
            stockOnHand = None

        # 卖方
        try:
            seller = res_html.xpath('string(//div[@id="merchant-info"])')
            seller = seller.replace("\n", "").split("Reviews")[0].strip()
            if not seller:
                try:
                    seller = res_html.xpath('string(//span[@id="merchant-info"])')
                    seller = seller.replace("\n", "").split("Reviews")[0].strip()
                except:
                    seller = None

        except:
            seller = None

        try:
            seller_cls = seller_handle(seller)
        except:
            seller_cls = None

        sales_est = None
        
        # 销量修正，实际反馈发现，销量预测头部偏高，中部偏低，做出微调
        if category_main and rank_main:
            try:
                sales_est = int(get_sales(cate=category_main, rank=rank_main))
                if sales_est >= 2000:
                    sales_est = int(sales_est*0.9)
                elif sales_est >= 1000:
                    sales_est = int(sales_est*1.25)
                else:
                    sales_est = int(sales_est*1.5)
                time.sleep(1)
                print("sales:",sales_est)
            except:
                pass

        each_detail_list = (goods_pic_url,goods_title, ASIN, brand, ad_plus, goods_price, choose_kind, seller, seller_cls,
                            rank_in_HK, date_on_shelf, stockOnHand, goods_review_count,product_dimensions,package_dimensions,
                            product_weight, ship_weight, goods_review_star, category_main, rank_main, sales_est, high_fre_words ,multi_asin, goods_each_ranks)

        if goods_title:
            self.detail_list.append(each_detail_list)


        # 写入数据库 
        if ASIN:
            # try:
            cs = self.conn.cursor()
            cs.execute('select * from amazon_test.goods_detail where goods_detail.ASIN=(%s)',ASIN)
            result = cs.fetchone()
            if result:
                update_sql = 'update goods_detail set rank_in_HK=(%s), goods_review_count=(%s),goods_review_star=(%s), ' \
                             'category_main=(%s), rank_main=(%s), goods_price=(%s), seller_cls=(%s), sales_est=(%s), high_fre_words=(%s)' \
                             'where ASIN=(%s)'
                count = cs.execute(update_sql, (rank_in_HK, goods_review_count, goods_review_star, category_main, rank_main,
                                                goods_price, seller_cls, sales_est, str(high_fre_words), ASIN))
                self.conn.commit()
                print(count, "ASIN已存在，更新完毕")
                cs.close()
            # else:
            #     insert_sql = 'insert into amazon_test.goods_detail(pic, goods_title, ASIN, brand, goods_price, seller_cls,' \
            #                  ' category_main, rank_main, sales_est, rank_in_HK, date_on_shelf, goods_review_count, goods_review_star, ' \
            #                  'product_dimensions, package_dimensions, product_weight, ship_weight, goods_each_ranks, high_fre_words)' \
            #                  ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            else:
                insert_sql = 'insert into amazon_test.goods_detail(pic, goods_title, ASIN, brand, goods_price, seller_cls,' \
                             ' category_main, rank_main, sales_est, rank_in_HK, date_on_shelf, goods_review_count, goods_review_star, ' \
                             'product_dimensions, package_dimensions, product_weight, ship_weight, goods_each_ranks, high_fre_words)' \
                             ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                if goods_each_ranks:
                    sql_ranks = json.dumps(goods_each_ranks)
                else:
                    sql_ranks = ""
                print(type(rank_main))
                count = cs.execute(insert_sql, (goods_pic_url,goods_title, ASIN, brand, goods_price, seller_cls,
                             category_main, rank_main, sales_est, rank_in_HK, date_on_shelf, goods_review_count, goods_review_star,
                            product_dimensions, package_dimensions, product_weight, ship_weight, sql_ranks, str(high_fre_words)))
                self.conn.commit()
                # print(goods_each_ranks)
                print(count, "ASIN已添加")
                cs.execute('select count(*) from amazon_test.goods_detail')
                result = cs.fetchall()
                print(result)
                cs.close()

def pic_save(base_code, ASIN):

        import base64
        img_data = base64.b64decode(base_code)
        file = open(r"..\data\pic\\" + str(ASIN)+'.jpg', 'wb')
        file.write(img_data)
        file.close()

if __name__ == '__main__':

    goods_detail = GoodDetail()
    data_file = r"../data/category/Crib Bedding Sets_08_29_12_37.xlsx"
    # data_file = r'../data/goods_rank_list/sweatshirt blanket-08201239_with_ad.csv'
    # data = pd.read_csv(data_file)
    # data = pd.read_excel(data_file, encoding='utf-8', sheet_name='筛选数据')

    # for url in data['goods_url_full'][:61]:
    #     if url:
    #         print(url)
    #         goods_detail.get_detail(url)
    #         time.sleep(random.uniform(1.2,2.5))

    data = pd.read_excel(data_file, encoding='utf-8')
    for ASIN in data['ASIN'][:51]:

        if ASIN:
            url = "https://www.amazon.com/dp/" + str(ASIN)
            print(url)
            goods_detail.get_detail(url)
            time.sleep(random.uniform(1.2,2.5))

    details_pd = pd.DataFrame(goods_detail.detail_list,
                              columns=['goods_pic_url', 'goods_title', 'ASIN', 'brand', 'ad_plus', 'goods_price',
                                       'choose_kind','seller', 'seller_cls','rank_in_HK', 'date_on_shelf','stockOnHand', 'goods_review_count',
                                       'product_dimensions', 'package_dimensions','product_weight', 'ship_weight',
                                       'goods_review_star','category_main', 'rank_main', 'sales_est', 'high_fre_words','multi_asin','goods_each_ranks'])
    ranks_pd = pd.DataFrame(goods_detail.rank_list)
    aft = datetime.datetime.now().strftime('%m%d%H%M')

    for base_code_full, ASIN in zip(details_pd['goods_pic_url'], details_pd['ASIN']):
        try:
            if base_code_full:
                base_code = base_code_full.split(',')[1]
                pic_save(base_code, ASIN)
        except:
            print("保存图片出错")

    time.sleep(3)

    # abs_path为项目的跟路径，相当于域
    abs_path = os.path.abspath('../')
    details_pd['pic_url'] = abs_path + r"\data\pic\\" +  details_pd['ASIN'] + ".jpg"
    details_pd['pic_table_url'] = '<table> <img src=' + '\"' +details_pd['pic_url'] + '\"' +'height="140" >'
    file_name_new = r"..\data\goods_detail\\" + aft + "_with_ad.xlsx"
    last_pd = pd.concat([details_pd, ranks_pd],axis=1)
    last_pd.drop_duplicates(subset=['category_main','rank_main'], inplace=True)
    last_pd.to_excel(file_name_new,  encoding='utf-8', engine='xlsxwriter')