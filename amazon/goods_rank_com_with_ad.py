import numpy as np
import pandas as pd
import requests, lxml
from lxml import etree
import re, time, random, datetime
import urllib


class AmazonGoods:
    headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
    }
    proxies = {
        # "http": "http://49.86.181.43:9999",
        "http": "http://114.217.241.20:8118",
    }

    url_base = "https://www.amazon.com"
    s = requests.Session()
    s.headers.update(headers)
    s.get(url=url_base)

    def __init__(self):
        self.goods_list = []

    def get_goods(self, url):

        res = self.s.get(url, headers=self.headers)
        if res.status_code != 200:
            print("请求出错，状态码为：%s" % res.status_code)
            print(res.text)
            return
        print(url)
        res_html = res.text
        # with open(r'测试.html', 'w') as f:
        #     f.write(res_html)
        # print(res_html.title())
        html = etree.HTML(res_html)

        # 自然排名和广告排名
        con_list = html.xpath('//div[@class="sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32"]')
        print("共有自然商品：{}个".format(str(len(con_list))))
        ad_con_list = html.xpath('//div[@class="sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item sg-col-4-of-28 sg-col-4-of-16 AdHolder sg-col sg-col-4-of-20 sg-col-4-of-32"]')
        all_goods_list = con_list + ad_con_list

        for each in all_goods_list:
            if each in ad_con_list:
                ad_plus = 1
            else:
                ad_plus = 0
            # 商品名称
            goods_title = each.xpath(".//span[@class='a-size-base-plus a-color-base a-text-normal']/text()")[0]
            print(goods_title)
            #  goods_title_handle(goods_title)
            # 商品链接
            goods_url = each.xpath(".//a[@class='a-link-normal a-text-normal']/@href")
            try:
                goods_url_full = "https://www.amazon.com" + goods_url[0].split('ref')[0]
            except:
                goods_url_full = "https://www.amazon.com" + goods_url[0]

            # 图片链接
            #             goods_pic_url = each.xpath(".//img/@src")[0]
            #             print(goods_pic_url.split("/")[-1])
            #             res_pic = self.s.get(goods_pic_url, headers=self.headers, proxies=self.proxies, verify=False)
            #             file_name = 'data/pic/swaddle blanket/' + goods_pic_url.split("/")[-1]
            #             with open(file_name, "wb") as f:
            #                 f.write(res_pic.content)
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


    goods = AmazonGoods()
    key_words = "wind chimes"
    for page in range(1, 3):
        if page == 1:
            url = "https://www.amazon.com/s?k=" + urllib.parse.quote(key_words)
            goods.get_goods(url)
            time.sleep(random.uniform(1.2, 2.4))
        else:
            url = "https://www.amazon.com/s?k=" + urllib.parse.quote(key_words) + "&page=" + str(page)
            goods.get_goods(url)
            time.sleep(random.uniform(1.2, 2.4))
        time.sleep(random.random())
    goods_pd = pd.DataFrame(goods.goods_list, columns=['goods_title', 'goods_url_full', 'price_whole', 'price_fraction', 'ad_plus', 'reviews'])
    aft = datetime.datetime.now().strftime('%m%d%H%M')
    file_name = r"..\data\goods_rank_list/" + key_words + "_" + aft + "_with_ad.csv"
    goods_pd.to_csv(file_name, encoding='utf-8')