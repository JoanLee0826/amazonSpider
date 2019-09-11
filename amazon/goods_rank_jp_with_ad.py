import numpy as np
import pandas as pd
import requests, lxml
from lxml import etree
import re, time, random, datetime


class AmazonGoods:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"
    }
    proxies = {
        "http": "http://114.239.3.156:9999",
    }

    url_base = "https://www.amazon.co.jp"
    s = requests.Session()
    s.get(url=url_base, headers=headers, proxies=proxies, verify=False)

    def __init__(self):
        self.goods_list = []


    def get_goods(self, url):

        res = self.s.get(url, headers=self.headers, proxies=self.proxies, verify=False)
        if res.status_code != 200:
            print("请求出错，状态码为：%s" % res.status_code)
            print(res.text)
            return

        res_html = res.text
        html = etree.HTML(res_html)

        # 自然排名和广告排名
        con_list = html.xpath('//div[@class="sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item sg-col-4-of-28'
                              ' sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32"]')
        ad_con_list = html.xpath('//div[@class="sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item '
                                 'sg-col-4-of-28 sg-col-4-of-16 AdHolder sg-col sg-col-4-of-20 sg-col-4-of-32"]')
        all_goods_list = con_list + ad_con_list
        for each in all_goods_list:

            if  each in ad_con_list:
                ad_plus = 1
            else:
                ad_plus = 0
            # 商品名称
            goods_title = each.xpath(".//span[@class='a-size-base-plus a-color-base a-text-normal']/text()")[0]
            #  goods_title_handle(goods_title)
            # 商品链接
            goods_url = each.xpath(".//a[@class='a-link-normal a-text-normal']/@href")
            goods_url_full = self.url_base + goods_url[0]

            # # 图片链接
            # goods_pic_url = each.xpath(".//img/@src")[0]
            # print(goods_pic_url.split("/")[-1])
            # res_pic = self.s.get(goods_pic_url, headers=self.headers, proxies=self.proxies, verify=False)
            # file_name = 'data/pic/swaddle blanket/' + goods_pic_url.split("/")[-1]
            # with open(file_name, "wb") as f:
            #     f.write(res_pic.content)
            # 商品价格 整数部分
            try:
                price_whole = each.xpath(".//span[@class='a-price-whole']/text()")[0]
            except:
                price_whole = None
            # 商品价格 小数部分
            try:
                price_fraction = each.xpath(".//span[@class='a-price-fraction']/text()")[0]
            except:
                price_fraction = None
            #  star = each.xpath('.//span[class="a-icon-alt"]/text()')

            # 商品的评论数
            try:
                reviews = each.xpath(".//span[@class='a-size-base']/text()")[0]
            except:
                reviews = None

            # 商品信息列表
            each_goods_list = [goods_title, goods_url_full, price_whole, price_fraction, ad_plus, reviews]
            self.goods_list.append(each_goods_list)
            print(len(self.goods_list))


if __name__ == '__main__':

    data_path = r'E:\爬虫pycharm\data\\'
    goods = AmazonGoods()
    key_words = "珪藻土 バスマット"
    for page in range(1, 5):
        if page == 1:
            # url = "https://www.amazon.com/s?k=" + key_words
            url = "https://www.amazon.co.jp/s?k=" + key_words
            goods.get_goods(url)
            time.sleep(random.random())
        else:
            # url = "https://www.amazon.com/s?k=" + key_words + "&page=" + str(page)
            url = "https://www.amazon.co.jp/s?&k=" + key_words + "&page=" + str(page)
            goods.get_goods(url)
            time.sleep(random.random())
        # print("page-%d-finish" % page)
        time.sleep(random.random())
    goods_pd = pd.DataFrame(goods.goods_list, columns=['goods_title', 'goods_url_full', 'price_whole', 'price_fraction', 'ad_plus', 'reviews'])
    aft = datetime.datetime.now().strftime('%m%d%H%M')
    file_name = data_path + "goods_rank_list/" + key_words + "-" + aft + "_with_ad.csv"
    goods_pd.to_csv(file_name, encoding='utf-8')