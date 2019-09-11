import pandas as pd
import numpy as np
import requests
from lxml import etree
import re, time, random, datetime
from queue import Queue
import threading
import  sys

class Review:

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }

    proxies = {
        "http": "http://117.91.131.74:9999",
    }
    def __init__(self, domain):
        self.view_list = []
        self.page_list = []
        self.url_queue = Queue()

        if domain.strip().lower() == 'jp':
            self.row_url = "https://www.amazon.co.jp"
        else:
            self.row_url = "https://www.amazon.com"

        self.s = requests.Session()

        self.s.get(url=self.row_url, headers=self.headers, proxies=self.proxies)

    def get_review(self, url):
        res = self.s.get(url, headers=self.headers, proxies=self.proxies)
        if res.status_code != 200:
            print("请求出错，状态码为：%s" % res.status_code)
            print(res.text)
            return

        res_html = etree.HTML(res.text)
        # 商品评价名称
        view_goods = res_html.xpath('//span[@class="a-list-item"]/a/text()')[0]
        # 商品评价容器
        view_con = res_html.xpath('//div[@class="a-section review aok-relative"]')

        for each_view in view_con:
            # 评价人
            view_name = each_view.xpath('.//span[@class="a-profile-name"]/text()')[0]
            view_star_raw = each_view.xpath('.//div[@class="a-row"]/a[@class="a-link-normal"]/@title')[0]
            # 评价星级
            view_star = view_star_raw.split(' ')[0]
            # 评价title
            view_title = each_view.xpath('.//a[@data-hook="review-title"]/span/text()')[0]
            # 评价日期
            view_date = each_view.xpath('.//span[@data-hook="review-date"]/text()')[0]
            view_format = each_view.xpath('.//a[@data-hook="format-strip"]/text()')
            view_colour = None
            view_size = None
            for each in view_format:
                if re.search("color", each, re.I) or re.search("colour", each, re.I):
                    view_colour = each.split(':')[1].strip()
                if re.search("size", each, re.I) or re.search('style', each, re.I):
                    view_size = each.split(":")[1].strip()
            # 评价内容
            view_body = each_view.xpath('string(.//span[@data-hook="review-body"]/span)')

            # 评价有用数量
            try:
                view_useful_raw = each_view.xpath('.//span[@data-hook="helpful-vote-statement"]/text()')[0]
                view_useful = view_useful_raw.split(' ')[0]
            except:
                view_useful = '0'
            # 商品的评价信息表
            each_view_list = [view_goods, view_name, view_star, view_title, view_date, view_colour, view_size,
                              view_body, view_useful]
            self.view_list.append(each_view_list)
        # print(self.view_list[-1])

    def run(self, data):
        goods_data = pd.read_excel(data, encoding='utf-8')
        base_url =  self.row_url + "/product-reviews/"
        # goods_data.drop_duplicates(subset=['r','评价数量'],inplace=True)
        # goods_data = goods_data['classfication'] == ''
        for  each_url, each_count in zip(goods_data['ASIN'][28:30], goods_data['goods_review_count'][28:30]):
            if each_url and int(each_count) > 0:
                if int(each_count) % 10 == 0:

                    end_page = int(each_count) // 10 + 1
                else:
                    end_page = int(each_count) // 10 + 2

                for page in range(1, end_page):
                    if page == 1:
                        url = base_url + each_url
                    else:
                        url = base_url + each_url + '?pageNumber=' + str(page)
                    self.url_queue.put(url)
                    print("review_page_%d" % page, url)

        time.sleep(1.5)

        while True:
            try:
                review_threads = [threading.Thread(target=self.get_review, args=(self.url_queue.get(),))
                                  for m in range(30) if not self.url_queue.empty()]
                for each in review_threads:
                    each.start()
                print("队列剩余数量",self.url_queue.qsize())

                for each in review_threads:
                    each.join()
            except:
                print("请求链接出错，重试中...")
                pass
            time.sleep(random.uniform(0.5,2.1))

            if self.url_queue.empty():
                break

        view_goods_pd = pd.DataFrame(self.view_list,
                                     columns=['review_goods', 'review_name', 'review_star', 'review_title',
                                              'review_date', 'review_colour', 'review_size', 'review_body',
                                              'review_useful'])
        view_goods_pd.drop_duplicates(subset=['review_name','review_date','review_body'],inplace=True)
        aft = datetime.datetime.now().strftime('%m%d%H%M')
        file_name = 'E:\爬虫pycharm\data\goods_review\\' + "reviews-" + aft + ".xlsx"
        view_goods_pd.to_excel(file_name, encoding='utf-8', engine='xlsxwriter')
        print("共获取评论数量：",len(self.view_list))



if __name__ == '__main__':


    data = r"../data/category/Kid's Weighted Blankets_08_28_13_22.xlsx"
    review = Review(domain='com')
    review.run(data=data)
