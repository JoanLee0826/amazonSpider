import numpy as np
import pandas as pd
import requests, lxml
from lxml import etree
import re, time, random, datetime
import pymysql
import os

head_user_agent = ['Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                       'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                       'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
                       'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11']


def weight_handle(weight):
    # 把kg g 都转化为数字存储
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
    row_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    }
    sales_url = "https://amzscout.net/extensions/scoutlite/v1/sales?"
    full_url = sales_url + "domain=COM&category=" + urllib.parse.quote(cate)+ "&rank=" + str(rank)
    print(full_url)
    s.headers.update(row_headers)
    res = s.get(full_url, timeout=10)
    try:
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
    s.headers.update({'User-Agent': random.choice(head_user_agent)})
    s.get(url=url_base, verify=False)

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
                print('该链接:' + url + '访问出错次数超过5次, 请手动尝试添加')
                return
            self.get_detail(url)

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
            multi_asin = list(set(sort_list.append(ASIN)))
        except:
            multi_asin = list(set(sort_list))
        print("-----------")
        print(multi_asin)
        print("-----------")
        product_dimensions = item.get('Product Dimensions', None)
        package_dimensions = item.get('Package Dimensions', None)
        product_weight = item.get('Item Weight', None)
        date_on_shelf = item.get('Date first listed on Amazon', None)
        if not date_on_shelf:
            date_on_shelf = item.get('date_on_shelf', None)

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

        rank_in_hk = None
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
                        rank_in_hk = int(goods_rank_num)
                    except:
                        rank_in_hk = None

            self.rank_list.append(goods_each_ranks)
            print(self.rank_list[-1])


            try:
                category_main = list(self.rank_list[-1].keys())[0]
                rank_main = int(list(self.rank_list[-1].values())[0])
            except:
                category_main, rank_main = None, None
            # print(category_main, rank_main)
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

        seller_name, seller_months, selelr_review_count = None, None, None
        if seller_cls == 'FBA' or 'FBM':
            try:
                seller_href = res_html.xpath("//div[@id='merchant-info']/a[1]/@href")[0]
                seller_url = "https://www.amazon.com" + seller_href
                seller_name, seller_months, selelr_review_count = seller_check(seller_url)
            except:
                pass
        sales_est = None
        if category_main and rank_main:
            print(category_main, rank_main, '销量预测中...')
            try:
                sales_est = int(get_sales(cate=category_main, rank=rank_main))
                # if sales_est >= 2000:
                #     sales_est = int(sales_est*1)
                # elif sales_est >= 1000:
                #     sales_est = int(sales_est*1.15)
                # else:
                #     sales_est = int(sales_est*1.25)
                # time.sleep(random.random())
                # print("sales:",sales_est)
            except:
                print(ASIN,'查询销量出错')
                pass

        each_detail_list = (goods_pic_url,goods_title, ASIN, brand, ad_plus, goods_price, choose_kind,
                            seller, seller_cls, seller_name, seller_months, selelr_review_count,
                            rank_in_hk, date_on_shelf, stockOnHand, goods_review_count,product_dimensions,
                            package_dimensions,product_weight, ship_weight, goods_review_star, category_main,
                            rank_main, sales_est, high_fre_words, multi_asin, goods_each_ranks)

        if goods_title:
            self.detail_list.append(each_detail_list)

        if ASIN:
            # try:
            cs = self.conn.cursor()
            cs.execute('select * from amazon_test.goods_detail where goods_detail.ASIN=(%s)', ASIN)
            result = cs.fetchone()
            if result:
                update_sql = 'update goods_detail set rank_in_HK=(%s), goods_review_count=(%s),goods_review_star=(%s), ' \
                             'category_main=(%s), rank_main=(%s), goods_price=(%s), seller_cls=(%s), sales_est=(%s), high_fre_words=(%s)' \
                             'where ASIN=(%s)'
                count = cs.execute(update_sql, (rank_in_hk, goods_review_count, goods_review_star, category_main, rank_main,
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
                count = cs.execute(insert_sql, (goods_pic_url,goods_title, ASIN, brand, goods_price, seller_cls,
                             category_main, rank_main, sales_est, rank_in_hk, date_on_shelf, goods_review_count, goods_review_star,
                            product_dimensions, package_dimensions, product_weight, ship_weight, sql_ranks, str(high_fre_words)))

                try:
                    self.conn.commit()
                except:
                    self.conn.rollback()
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


def seller_check(url):
    print("卖家年评论数获取中...")
    s = requests.Session()
    s.headers.update({'User-Agent': random.choice(head_user_agent)})
    res = s.get(url)
    if res.status_code != 200:
        print('{}卖家信息查询出错'.format(url))
        return None
    res_html = etree.HTML(res.text)

    seller_name, seller_months, seller_count = None, None, None
    try:
        seller_name = res_html.xpath("//h1[@id='sellerName']/text()")[0]
    except:
        pass

    try:
        seller_review_str = res_html.xpath("//a[@class='a-link-normal feedback-detail-description']/text()")[0]
    except:
        return

    try:
        count_patt = re.compile('in the last (.*) months \((.*) ratings\)')
        a, b = re.search(count_patt, seller_review_str).groups()
        seller_months, seller_count = int(a), int(b)
    except:
        pass

    if not seller_count:
        try:
            another_patt = re.compile('(\d+) total ratings\)')
            seller_months = 0
            seller_count = int(re.search(another_patt, seller_review_str).group(1))
        except:
            pass

    return seller_name, seller_months, seller_count


def main(file_path):
    goods_detail = GoodDetail()

    if file_path.endswith('csv'):
        data = pd.read_csv(file_path)
        for url in data['goods_url_full'][20:30]:
            if url:
                print(url)
                goods_detail.get_detail(url)
                time.sleep(random.random())
    if file_path.endswith('xlsx'):
        data = pd.read_excel(file_path, encoding='utf-8')
        for ASIN in data['ASIN']:
            if ASIN:
                url = "https://www.amazon.com/dp/" + str(ASIN)
                print(url)
                goods_detail.get_detail(url)
                time.sleep(random.random())

    details_pd = pd.DataFrame(goods_detail.detail_list,
                              columns=['goods_pic_url', 'goods_title', 'ASIN', 'brand', 'ad_plus', 'goods_price',
                                       'choose_kind', 'seller', 'seller_cls', 'seller_name', 'seller_months',
                                       'selelr_review_count', 'rank_in_HK', 'date_on_shelf', 'stockOnHand',
                                       'goods_review_count', 'product_dimensions', 'package_dimensions',
                                       'product_weight', 'ship_weight', 'goods_review_star', 'category_main',
                                       'rank_main', 'sales_est', 'high_fre_words', 'multi_asin', 'goods_each_ranks'])
    # ranks_pd = pd.DataFrame(goods_detail.rank_list)
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
    details_pd['pic_url'] = abs_path + r"\data\pic\\" + details_pd['ASIN'] + ".jpg"
    details_pd['pic_table_url'] = '<table> <img src=' + '\"' + details_pd['pic_url'] + '\"' + 'height="140" >'
    file_name_new = r"..\data\goods_detail\\" + aft + "_with_ad.xlsx"
    # last_pd = pd.concat([details_pd, ranks_pd], axis=1)
    details_pd.drop_duplicates(subset=['category_main', 'rank_main'], inplace=True)
    details_pd.to_excel(file_name_new, encoding='utf-8', engine='xlsxwriter')


if __name__ == '__main__':
    file_path = r'../data/goods_rank_list/milestone blanket_11191743_with_ad.csv'
    main(file_path=file_path)

